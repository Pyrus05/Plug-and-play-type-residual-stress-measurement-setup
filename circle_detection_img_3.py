import cv2
import numpy as np
import sys

def main(image_path):
    print(f"Loading image: {image_path}")
    
    # Load the image
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Error: Unable to load image {image_path}")
        sys.exit(1)
    
    print("Image loaded successfully.")
    print(f"Original image dimensions: {image.shape[1]}x{image.shape[0]}")
    
    # Resize image while maintaining aspect ratio (optional)
    desired_width = 1080
    scale_factor = desired_width / image.shape[1]
    new_height = int(image.shape[0] * scale_factor)
    image = cv2.resize(image, (desired_width, new_height))
    print(f"Resized image to: {image.shape[1]}x{image.shape[0]}")
    
    # Save debug image
    cv2.imwrite("debug_original.jpg", image)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print("Converted image to grayscale.")
    
    # Save grayscale image for debugging
    cv2.imwrite("debug_gray.jpg", gray)
    
    # Apply median blur
    gray = cv2.medianBlur(gray, 7)
    print("Applied median blur.")
    
    # Save blurred image for debugging
    cv2.imwrite("debug_blur.jpg", gray)
    
    # Perform edge detection using Canny
    edges = cv2.Canny(gray, 100, 200)
    print("Performed Canny edge detection.")
    
    # Save edges image for debugging
    cv2.imwrite("debug_edges.jpg", edges)
    
    # Detect circles using Hough Circle Transform
    print("Running HoughCircles detection...")
    circles = cv2.HoughCircles(
        gray,  # Using grayscale image instead of edges
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=50,
        param1=200,  # Adjusted lower edge detection threshold
        param2=45,  # Adjusted detection confidence
        minRadius=0,
        maxRadius=100
    )
    
    if circles is not None:
        print(f"Detected {len(circles[0])} circles.")
        circles = np.uint16(np.around(circles))
        for (x, y, r) in circles[0, :]:
            print(f"Circle detected at X={x}, Y={y}, Radius={r}")
            # Draw the outer circle
            cv2.circle(image, (x, y), r, (0, 255, 0), 2)
            # Draw the center of the circle
            cv2.circle(image, (x, y), 2, (0, 0, 255), 3)
    else:
        print("No circles detected.")
    
    # Save final output image for debugging
    cv2.imwrite("debug_output.jpg", image)
    
    # Display the edges and final output simultaneously
    combined = np.hstack((cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR), image))
    cv2.imshow("Edges and Circle Detection", combined)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("Program finished.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <image_path>")
        sys.exit(1)
    
    main(sys.argv[1])
