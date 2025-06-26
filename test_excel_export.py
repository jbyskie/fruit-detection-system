#!/usr/bin/env python3
"""
Test script for Excel export functionality
"""

import sys
import os
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from excel_template import FruitDetectionExcelTemplate, create_detection_export, create_summary_export

def test_excel_template():
    """Test the Excel template functionality"""
    
    # Mock detection data
    class MockDetection:
        def __init__(self, fruit_type, ripeness, confidence, timestamp, image_path):
            self.fruit_type = fruit_type
            self.ripeness = ripeness
            self.confidence = confidence
            self.timestamp = timestamp
            self.image_path = image_path
    
    class MockUser:
        def __init__(self, username):
            self.username = username
            self.created_at = datetime.now() - timedelta(days=30)
    
    # Create mock data
    detections = [
        MockDetection("Mangosteen", "ripe", 0.95, datetime.now() - timedelta(hours=1), "test1.jpg"),
        MockDetection("Mangosteen", "unripe", 0.87, datetime.now() - timedelta(hours=2), "test2.jpg"),
        MockDetection("Mangosteen", "ripe", 0.72, datetime.now() - timedelta(hours=3), "test3.jpg"),
    ]
    
    user = MockUser("testuser")
    filters = {"ripeness": "all", "date_from": "2024-01-01"}
    
    # Test detection export
    print("Testing detection export...")
    try:
        output, filename = create_detection_export(detections, user, filters)
        print(f"✓ Detection export successful: {filename}")
        print(f"  File size: {len(output.getvalue())} bytes")
    except Exception as e:
        print(f"✗ Detection export failed: {e}")
        return False
    
    # Test summary export
    print("Testing summary export...")
    try:
        summary_data = {
            'Total Detections': 150,
            'Today Detections': 5,
            'This Week Detections': 25,
            'This Month Detections': 120,
            'Ripe Mangosteen': 80,
            'Unripe Mangosteen': 70,
            'Average Confidence (%)': '85.5%',
            'Account Created': '2024-01-01',
            'Report Generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        output, filename = create_summary_export(summary_data, user)
        print(f"✓ Summary export successful: {filename}")
        print(f"  File size: {len(output.getvalue())} bytes")
    except Exception as e:
        print(f"✗ Summary export failed: {e}")
        return False
    
    # Test template class directly
    print("Testing template class...")
    try:
        template = FruitDetectionExcelTemplate()
        output = template.create_detection_report(detections, user, filters)
        filename = template.generate_filename("Test_Report")
        print(f"✓ Template class test successful: {filename}")
        print(f"  File size: {len(output.getvalue())} bytes")
    except Exception as e:
        print(f"✗ Template class test failed: {e}")
        return False
    
    print("\n🎉 All Excel export tests passed!")
    return True

if __name__ == "__main__":
    print("Testing Fruit Detection System Excel Export Functionality")
    print("=" * 60)
    
    success = test_excel_template()
    
    if success:
        print("\n✅ Excel export functionality is working correctly!")
        print("You can now use the export features in the web application.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1) 