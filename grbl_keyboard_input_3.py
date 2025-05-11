import serial
import time
import keyboard  # Library for capturing keyboard input

# Replace 'COM11' with your serial port (e.g., '/dev/ttyUSB0' on Linux or 'COMx' on Windows)
ser = serial.Serial('COM11', 115200)
time.sleep(2)  # Wait for the connection to initialize

def send_gcode_command(command):
    command = command.strip() + '\n'
    ser.write(command.encode())  # Send G-code command
    response = ser.readline().decode().strip()  # Read GRBL's response
    print("Response:", response)

try:
    # Initialize GRBL by sending a newline
    ser.write(b"\r\n\r\n")
    time.sleep(2)  # Wait for GRBL to initialize
    ser.flushInput()  # Flush startup message

    # Set to relative positioning and millimeters
    send_gcode_command("G91")  # Set to relative positioning
    send_gcode_command("G21")  # Set units to millimeters

    # Initial move increment
    increment = 1  # Move 1 mm per key press

    print("Use arrow keys to move X and Y axes.")
    print("Use 'Shift' for Z up and 'Left Ctrl' for Z down.")
    print("Press '+' or '-' to increase/decrease increment.")
    print("Press 's' to set current position as zero.")
    print("Press 'g' to go to zero position.")
    print("Press 'esc' to quit.")

    # Variables to track zero position
    x_zero, y_zero, z_zero = 0, 0, 0

    while True:
        # Move X and Y with arrow keys
        if keyboard.is_pressed('up'):
            send_gcode_command(f"G1 Y{increment} F500")  # Move Y+ (up)
            time.sleep(0.1)
        elif keyboard.is_pressed('down'):
            send_gcode_command(f"G1 Y{-increment} F500")  # Move Y- (down)
            time.sleep(0.1)
        elif keyboard.is_pressed('left'):
            send_gcode_command(f"G1 X{-increment} F500")  # Move X- (left)
            time.sleep(0.1)
        elif keyboard.is_pressed('right'):
            send_gcode_command(f"G1 X{increment} F500")  # Move X+ (right)
            time.sleep(0.1)

        # Move Z axis with Shift (up) and Left Ctrl (down)
        elif keyboard.is_pressed('shift'):
            send_gcode_command(f"G1 Z{increment} F500")  # Move Z+ (up)
            time.sleep(0.1)
        elif keyboard.is_pressed('ctrl'):
            send_gcode_command(f"G1 Z{-increment} F500")  # Move Z- (down)
            time.sleep(0.1)

        # Increase or decrease increment
        elif keyboard.is_pressed('+'):
            increment += 1.0  # Increase increment by 0.1 mm
            print(f"Increment increased to {increment:.1f} mm")
            time.sleep(0.2)
        elif keyboard.is_pressed('-') and increment > 0.1:
            increment -= 1.0  # Decrease increment by 0.1 mm (minimum of 0.1 mm)
            print(f"Increment decreased to {increment:.1f} mm")
            time.sleep(0.2)

        # Set current position as zero
        elif keyboard.is_pressed('s'):
            x_zero, y_zero, z_zero = 0, 0, 0
            send_gcode_command("G92 X0 Y0 Z0")  # Set current position as zero
            print("Current position set as zero.")
            time.sleep(0.5)

        # Go to zero position
        elif keyboard.is_pressed('g'):
            send_gcode_command("G90")  # Switch to absolute positioning
            send_gcode_command(f"G1 X{x_zero} Y{y_zero} Z{z_zero} F500")  # Move to zero
            send_gcode_command("G91")  # Switch back to relative positioning
            print("Moved to zero position.")
            time.sleep(0.5)

        # Exit control
        elif keyboard.is_pressed('esc'):
            print("Exiting control.")
            break

except Exception as e:
    print("Error:", e)
finally:
    ser.close()  # Close the serial connection
