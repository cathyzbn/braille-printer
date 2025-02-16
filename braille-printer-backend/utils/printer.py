from typing import List
import serial
import time
import threading
from enum import Enum

from utils.braille_to_gcode import DotPosition, GcodeAction, dot_pos_to_gcode

# Replace with your printer's correct port
port = "/dev/tty.usbserial-0001"
baud_rate = 250000  # Adjust this to match your printer's baud rate

class PrintStatus(Enum):
    IDLE = "idle"
    PRINTING = "printing" 
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"

def calculate_checksum(command):
    """Calculate Marlin-style checksum for a G-code command."""
    checksum = 0
    # Include the space after the command in checksum calculation
    for c in command:
        checksum ^= ord(c)
    return checksum & 0xFF  # Ensure 8-bit result

class PrinterConnection:
    def __init__(self, port, baud_rate):
        self.port = port
        self.baud_rate = baud_rate
        self.ser = None
        self.line_number = 0
        self.E_steps_per_unit = 400.0
        self.E_steps_per_degree = 8 * 0.9
        self.status = PrintStatus.IDLE
        self.print_thread = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

    def connect(self):
        """Establish connection and perform initial handshake."""
        print("Connecting to printer...")
        self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
        self.ser.reset_input_buffer()
        
        if not self.wait_for_start():
            raise Exception("Printer did not send 'start' within timeout.")
        
        print("Printer is ready! Performing handshake...")
        
        # Start fresh with line numbers
        self.line_number = 0
        
        # Reset line numbers - keep trying until we get a clean OK
        while True:
            self.send_command("M110 N0")
            # Send a test command to verify synchronization
            if self.send_command("M115"):
                break
            time.sleep(0.1)
        
        # Now that we're synchronized, enable debug output
        self.send_command("M111 S6")
        print("Handshake complete!")

    def initialize(self):
        self.send_command("G91")     # Set relative positioning
        self.send_command("G1 Z10 F800")
        self.send_command("G90")     # Set absolute positioning
        self.send_command("M83")     # Set relative extrusion
        self.send_command("M302 S0") # Allow cold extrusion at any temperature
        self.send_command("G28")     # Zero all axes
        # Calibrate extrusion
        for _ in range(2):
            self.send_command("G1 E2.2 F200")
            self.send_command("G1 E-2.2 F200")
        self.send_command("G1 E1.5 F200")
        self.send_command("G1 Z3 F800")
        # self.send_command("G1 Z10 F800")
        # input("Press Enter to continue...")

    def cleanup(self):
        self.send_command("G1 Z10 F800") # Move z axis up
        self.send_command("G28 X0 Y0")   # Zero X and Y
        self.send_command("G1 Z50 F800") # Move z axis up so can easily remove page

    def wait_for_start(self, timeout=10):
        """Wait for the printer to send 'start' after connecting."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.ser.in_waiting:
                response = self.ser.readline().decode().strip()
                print(f"Printer: {response}")
                if "start" in response.lower():
                    return True
        return False

    def send_command(self, command, wait_for_ok=True):
        """Send a G-code command with line number and checksum."""
        while True:  # Keep trying until command is accepted
            if command.startswith('N'):
                formatted_command = command
            else:
                formatted_command = f"N{self.line_number} {command}"
            
            # Add checksum if not already present
            if '*' not in formatted_command:
                # Calculate checksum only for the part before any existing *
                checksum_part = formatted_command.split('*')[0]
                checksum = calculate_checksum(checksum_part)
                formatted_command = f"{checksum_part}*{checksum}"  # Removed extra space before *
                print(f"Debug - Command: '{checksum_part}', Checksum: {checksum}")  # Debug line

            self.ser.write((formatted_command + "\n").encode())
            print(f"Sent: {formatted_command}")

            if not wait_for_ok:
                break

            # Wait for response
            while True:
                response = self.ser.readline().decode().strip()
                if not response:
                    continue
                
                print(f"Printer: {response}")
                
                # Check for resend requests
                if "resend:" in response.lower():
                    self.line_number = int(response.lower().split("resend:")[1].strip())
                    break
                elif "error:checksum mismatch" in response.lower():
                    # Extract last line number and set our counter to next line
                    try:
                        last_line = int(response.lower().split("last line:")[1].strip())
                        self.line_number = last_line + 1
                    except (ValueError, IndexError):
                        self.line_number = 1  # Reset to 1 if we can't parse the line number
                    break
                elif "error:line number is not" in response.lower():
                    # Similar handling as checksum mismatch
                    try:
                        last_line = int(response.lower().split("last line:")[1].strip())
                        self.line_number = last_line + 1
                    except (ValueError, IndexError):
                        self.line_number = 1
                    break
                elif "echo:  m92 " in response.lower():
                    gcode = response.replace("echo:  m92 ", "").strip()
                    parts = gcode.split(" ")
                    for part in parts:
                        if part.startswith("E"):
                            self.E_steps_per_unit = float(part.replace("E", ""))
                            print(f"E_steps_per_unit: {self.E_steps_per_unit}")
                            break
                
                if "ok" in response.lower():
                    self.line_number += 1  # Only increment after confirmed OK
                    return True
                
                # If we get here, keep reading responses until we get ok/error
                continue
            
            # If we broke out of the inner while loop, it means we need to resend
            continue

    def close(self):
        """Close the printer connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Connection closed.")

    def stop(self):
        """Stop the current print job."""
        self._stop_event.set()
        if self.print_thread:
            self.print_thread.join()
        self._stop_event.clear()
        self.status = PrintStatus.IDLE
        self.cleanup()

    def pause(self):
        """Pause the current print job."""
        if self.status == PrintStatus.PRINTING:
            self._pause_event.set()
            self.status = PrintStatus.PAUSED

    def resume(self):
        """Resume the paused print job."""
        if self.status == PrintStatus.PAUSED:
            self._pause_event.clear()
            self.status = PrintStatus.PRINTING

    def get_status(self):
        """Get the current status of the printer."""
        return self.status

def print_gcode(gcode_actions: List[GcodeAction]):
    printer = PrinterConnection(port, baud_rate)
    
    def print_thread():
        try:
            printer.connect()
            printer.initialize()
            printer.status = PrintStatus.PRINTING
            
            for action in gcode_actions:
                if printer._stop_event.is_set():
                    break
                    
                while printer._pause_event.is_set():
                    time.sleep(0.1)
                    if printer._stop_event.is_set():
                        break
                        
                printer.send_command(action.command)
                
            if not printer._stop_event.is_set():
                printer.cleanup()
                printer.status = PrintStatus.COMPLETED
                
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            printer.status = PrintStatus.ERROR
        except Exception as e:
            print(f"Error: {e}")
            printer.status = PrintStatus.ERROR
        finally:
            printer.close()

    printer.print_thread = threading.Thread(target=print_thread)
    printer.print_thread.start()
    return printer  # Return printer object so caller can control/monitor the print

def print_dots(dots: List[DotPosition]):
    gcode_actions = dot_pos_to_gcode(dots)
    return print_gcode(gcode_actions)

def main():
    printer = PrinterConnection(port, baud_rate)
    try:
        printer.connect()
        printer.initialize()

        # Example movement commands
        # printer.send_command("G90")         # Set absolute positioning
        # printer.send_command("M83")
        # printer.send_command("M302 S0")  # Allow cold extrusion at any temperature
        # printer.send_command("G28")         # Zero all axes
        # printer.send_command("G1 X10 Y10 Z10 F400") # Set X, Y, Z axis to 10mm at 400mm/s
        # printer.send_command("G1 E0.2 F800")
        # printer.send_command("G91")
        # printer.send_command("G1 Z-2 F100")
        # time.sleep(5)

        # printer.send_command("G1 E2 F200")

        printer.send_command("G1 E2 F800")
        printer.send_command("G1 X10 Y10 Z10 F400")
        printer.send_command("G1 E2 F800")
        printer.send_command("G1 X10 Y10 Z10 F400")
        printer.send_command("G1 E2 F800")

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        printer.close()

if __name__ == "__main__":
    main()
