import os
import cv2
import numpy as np
from app import app, detect_fruit

def test_detection():
    with app.app_context():
        # Test image path
        test_image_path = 'static/uploads/test_image.jpg'
        
        # Create a test image if it doesn't exist
        if not os.path.exists(test_image_path):
            print("Creating test image...")
            # Create a purple square on white background
            img = np.ones((300, 300, 3), dtype=np.uint8) * 255
            img[100:200, 100:200] = [128, 0, 128]  # Purple color
            cv2.imwrite(test_image_path, img)
            print(f"Test image created at: {test_image_path}")
        
        # Test detection
        print("\nTesting fruit detection...")
        result = detect_fruit(test_image_path)
        
        if result:
            print("\nDetection Results:")
            print(f"Fruit Type: {result['fruit_type']}")
            print(f"Ripeness: {result['ripeness']}")
            print(f"Confidence: {result['confidence']:.2f}")
            
            # Check if processed image exists
            processed_path = os.path.join('static/uploads', f"processed_{os.path.basename(test_image_path)}")
            if os.path.exists(processed_path):
                print(f"\nProcessed image saved at: {processed_path}")
            else:
                print("\nError: Processed image not found")
        else:
            print("\nError: Detection failed")

if __name__ == '__main__':
    # Ensure uploads directory exists
    os.makedirs('static/uploads', exist_ok=True)
    test_detection() 