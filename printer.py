import serial
import time

# Replace with your printer's correct port
port = "/dev/tty.usbserial-0001"
baud_rate = 250000  # Adjust this to match your printer's baud rate

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

def main():
    printer = PrinterConnection(port, baud_rate)
    try:
        printer.connect()

        # Example movement commands
        printer.send_command("G21")  # Set units to millimeters
        printer.send_command("G91")  # Set relative positioning
        printer.send_command("G1 Y10 F400")  # Move Y-axis
        printer.send_command("G90")  # Back to absolute positioning

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        printer.close()

if __name__ == "__main__":
    main()
