import time
import cv2
import numpy as np
import serial
import threading
from picamera2 import Picamera2
import keyboard

# Setup GRBL serial
ser = serial.Serial('/dev/ttyUSB0', 115200)
time.sleep(2)
ser.write(b"\r\n\r\n")
time.sleep(2)
ser.flushInput()

# Send G-code command
def send_gcode(cmd):
    ser.write((cmd.strip() + '\n').encode())
    print("Response:", ser.readline().decode().strip())

def wait_for_idle():
    while True:
        ser.write(b'?')  # Query status
        status = ser.readline().decode().strip()
        if "Idle" in status:
            break
        time.sleep(0.1)

# Flag to prevent repeated +X 70mm moves
alignment_executed = False

def camera_thread():
    global alignment_executed
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (1280, 720), "format": "RGB888"})
    picam2.configure(config)
    picam2.set_controls({"AfMode": 2, "AwbMode": 0})
    picam2.start()
    time.sleep(2)

    frame_width = 1280
    frame_height = 720
    camera_center = (frame_width // 2, frame_height // 2)

    mm_per_pixel = 0.01  # Adjust based on calibration
    tolerance_mm = 0.01  # Alignment tolerance

    while True:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        gray = cv2.medianBlur(gray, 7)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 50,
                                   param1=100, param2=45, minRadius=10, maxRadius=100)

        if circles is not None and not alignment_executed:
            circles = np.uint16(np.around(circles))
            for (x, y, r) in circles[0, :1]:  # First detected circle
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)

                dx_px = x - camera_center[0]
                dy_px = camera_center[1] - y

                dx_mm = dx_px * mm_per_pixel
                dy_mm = dy_px * mm_per_pixel

                print(f"[Circle] Offset: dx={dx_mm:.4f} mm, dy={dy_mm:.4f} mm")

                if abs(dx_mm) <= tolerance_mm and abs(dy_mm) <= tolerance_mm:
                    print("[Aligned] Circle is already centered.")
                    send_gcode("G1 X70 F1000")
                    wait_for_idle()
                    print("[Move] Gantry moved +X 70mm.")
                    alignment_executed = True  # Prevent repeat
                else:
                    gcode_cmd = f"G1 X{dx_mm:.2f} Y{dy_mm:.2f} F1000"
                    print(f"[Correction] Sending: {gcode_cmd}")
                    send_gcode(gcode_cmd)
                    wait_for_idle()
                    print("[Move] Circle aligned with camera center.")

        cv2.circle(frame, camera_center, 5, (255, 0, 0), -1)
        cv2.imshow("Circle Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    picam2.stop()
    cv2.destroyAllWindows()

# Keyboard Control Thread
def control_thread():
    send_gcode("G91")  # Relative
    send_gcode("G21")  # mm
    send_gcode("G92 X0 Y0 Z0")
    increment = 1

    while True:
        if keyboard.is_pressed('up'):
            send_gcode(f"G1 Y{increment} F500")
            time.sleep(0.1)
        elif keyboard.is_pressed('down'):
            send_gcode(f"G1 Y{-increment} F500")
            time.sleep(0.1)
        elif keyboard.is_pressed('left'):
            send_gcode(f"G1 X{-increment} F500")
            time.sleep(0.1)
        elif keyboard.is_pressed('right'):
            send_gcode(f"G1 X{increment} F500")
            time.sleep(0.1)
        elif keyboard.is_pressed('shift'):
            send_gcode(f"G1 Z{increment} F500")
            time.sleep(0.1)
        elif keyboard.is_pressed('ctrl'):
            send_gcode(f"G1 Z{-increment} F500")
            time.sleep(0.1)
        elif keyboard.is_pressed('esc'):
            print("Exiting control.")
            break

# Run Threads
if __name__ == "__main__":
    t1 = threading.Thread(target=camera_thread)
    t2 = threading.Thread(target=control_thread)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    ser.close()
