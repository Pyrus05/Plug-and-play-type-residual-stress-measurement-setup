import time
import cv2
import numpy as np
from picamera2 import Picamera2

def main():
    # Initialize Picamera2
    picam2 = Picamera2()

    # Configure camera settings
    camera_config = picam2.create_preview_configuration(
        main={"size": (1280, 720), "format": "RGB888"}  # Set resolution and color format
    )
    picam2.configure(camera_config)

    # Apply settings to improve image quality
    controls = {
        "AfMode": 2,  # Enable auto-focus
        "AwbMode": 0,  # Auto white balance to prevent blue tint
    }
    picam2.set_controls(controls)

    # Start the camera
    picam2.start()
    time.sleep(2)  # Allow camera to warm up

    while True:
        # Capture frame as a NumPy array
        frame = picam2.capture_array()

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)  # Ensure correct color conversion

        # Apply median blur
        gray = cv2.medianBlur(gray, 7)

        # Detect circles using Hough Circle Transform
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=50,
            param1=100,  # Edge detection threshold
            param2=45,   # Circle detection threshold
            minRadius=10,
            maxRadius=100
        )

        # If circles are detected, draw them
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for (x, y, r) in circles[0, :]:
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)  # Draw outer circle (green)
                cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)  # Draw center (red)

        # Display the frame with detected circles
        cv2.imshow("Circle Detection", frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
