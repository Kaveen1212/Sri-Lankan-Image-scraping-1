import sys
import subprocess
import os
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def check_python_version():
    print(f"Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ Python 3.6 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_dependencies():
    print(f"\nChecking dependencies...")
    required = ["selenium", "requests"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        install = input("Do you want to install them now? (y/n): ")
        if install.lower() == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed")
            return True
        return False
    return True

def check_chrome():
    print(f"\nChecking Chrome browser...")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        print("✅ Chrome and ChromeDriver are working")
        return True
    except Exception as e:
        print(f"❌ Chrome check failed: {e}")
        print("\nPossible solutions:")
        print("1. Make sure Chrome is installed")
        print("2. Download ChromeDriver that matches your Chrome version from:")
        print("   https://chromedriver.chromium.org/downloads")
        print("3. Add ChromeDriver to your PATH or use webdriver-manager package")
        return False

def check_proxy_list(proxy_list):
    if not proxy_list or len(proxy_list) == 0:
        print("\n⚠️ No proxies configured. Script will run without proxy.")
        return True
    
    print(f"\nFound {len(proxy_list)} proxies configured.")
    print(f"First few proxies: {', '.join(proxy_list[:3])}...")
    print("✅ Proxy list loaded successfully")
    return True

def check_permissions():
    print(f"\nChecking write permissions...")
    test_dir = "sri_lankan_images"
    try:
        os.makedirs(test_dir, exist_ok=True)
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✅ Write permissions OK")
        return True
    except Exception as e:
        print(f"❌ Permission check failed: {e}")
        return False

def main():
    print("=" * 50)
    print("Sri Lankan Image Downloader - System Check")
    print("=" * 50)
    
    # Run all checks
    checks = [
        check_python_version(),
        check_dependencies(),
        check_permissions()
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("✅ All checks passed! You're ready to run the script.")
        print("\nRun the image downloader with:")
        if platform.system() == "Windows":
            print("python direct_image_downloader.py")
        else:
            print("python3 direct_image_downloader.py")
    else:
        print("❌ Some checks failed. Please fix the issues before running the script.")
        
    print("=" * 50)

if __name__ == "__main__":
    main()
