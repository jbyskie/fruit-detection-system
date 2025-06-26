import cv2
import numpy as np
import os

def test_basic_image_processing():
    """Test basic image processing functionality"""
    # Create a test image
    test_image = np.zeros((300, 300, 3), dtype=np.uint8)
    test_image[100:200, 100:200] = [128, 0, 128]  # Purple square
    
    # Save test image
    test_path = "static/uploads/test_image.jpg"
    cv2.imwrite(test_path, test_image)
    print(f"Test image saved to: {test_path}")
    
    # Try to read the image
    img = cv2.imread(test_path)
    if img is None:
        print("Error: Could not read test image")
        return
    
    print(f"Test image read successfully. Shape: {img.shape}")
    
    # Try to convert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    print("HSV conversion successful")
    
    # Try to create a mask
    lower_purple = np.array([120, 50, 50])
    upper_purple = np.array([170, 255, 255])
    mask = cv2.inRange(hsv, lower_purple, upper_purple)
    print("Mask creation successful")
    
    # Try to find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Found {len(contours)} contours")
    
    # Try to draw bounding box
    if contours:
        x, y, w, h = cv2.boundingRect(contours[0])
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        print("Bounding box drawn successfully")
    
    # Try to save the result
    output_path = "static/uploads/test_output.jpg"
    success = cv2.imwrite(output_path, img)
    if success:
        print(f"Output image saved to: {output_path}")
    else:
        print("Failed to save output image")

if __name__ == '__main__':
    # Ensure uploads directory exists
    os.makedirs("static/uploads", exist_ok=True)
    
    # Run the test
    test_basic_image_processing() 