import serial
import time

# Replace '/dev/ttyUSB0' (Linux/macOS) or 'COM3' (Windows) with your printer's port
port = "/dev/tty.usbserial-0001"
baud_rate = 250_000  # Adjust this to match your printer's baud rate

try:
    # Open serial connection
    ser = serial.Serial(port, baud_rate, timeout=1)

    # Small delay to ensure connection is established
    time.sleep(2)

    # Send G-code command (move Y-axis slowly)
    gcode_command = "G91\nG1 Y5 F400\nG90\n"
    ser.write(gcode_command.encode())  # Send command
    print("Sent:", gcode_command.strip())

    # Read response (optional)
    response = ser.readlines()
    for line in response:
        print(line.decode().strip())

    # Close connection
    ser.close()

except serial.SerialException as e:
    print("Error:", e)
