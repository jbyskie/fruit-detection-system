import sys
import importlib
import os

def check_package(package_name):
    try:
        module = importlib.import_module(package_name)
        print(f"✓ {package_name} is installed (version: {getattr(module, '__version__', 'unknown')})")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False

def check_opencv():
    try:
        import cv2
        print(f"✓ OpenCV is installed (version: {cv2.__version__})")
        
        # Test basic OpenCV functionality
        test_image = cv2.imread("static/uploads/test_image.jpg")
        if test_image is not None:
            print("✓ OpenCV can read images")
        else:
            print("✗ OpenCV cannot read images")
            
        return True
    except Exception as e:
        print(f"✗ OpenCV error: {str(e)}")
        return False

def check_folders():
    folders = ['static', 'static/uploads']
    for folder in folders:
        if os.path.exists(folder):
            print(f"✓ Folder exists: {folder}")
            if os.access(folder, os.W_OK):
                print(f"✓ Folder is writable: {folder}")
            else:
                print(f"✗ Folder is NOT writable: {folder}")
        else:
            print(f"✗ Folder does NOT exist: {folder}")

def main():
    print("Checking Python version...")
    print(f"Python version: {sys.version}")
    print("\nChecking required packages...")
    
    packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'numpy',
        'sklearn',
        'PIL'
    ]
    
    all_packages_ok = all(check_package(pkg) for pkg in packages)
    
    print("\nChecking OpenCV...")
    opencv_ok = check_opencv()
    
    print("\nChecking folders...")
    check_folders()
    
    if all_packages_ok and opencv_ok:
        print("\nAll checks passed! The environment is properly set up.")
    else:
        print("\nSome checks failed. Please install missing packages or fix the issues.")

if __name__ == '__main__':
    main() 