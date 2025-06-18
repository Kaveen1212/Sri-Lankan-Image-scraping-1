from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import base64
import requests
from urllib.parse import urlparse
import random

# Setup proxy list - SOCKS proxies from socks-proxy.net (Updated at 2025-06-17)
PROXY_LIST = [
    "socks5://18.203.249.67:10010",
    "socks5://37.193.71.189:1080",
    "socks5://104.244.74.206:38118",
    "socks5://190.104.26.227:33638",
    "socks5://93.123.98.80:5678",
    "socks5://184.178.172.11:4145",
    "socks5://118.70.151.55:1080",
    "socks5://103.144.18.95:80",
    "socks5://103.169.254.155:1080",
    "socks5://190.14.5.163:5678",
    "socks5://184.181.217.194:4145",
    "socks5://91.199.139.246:1111",
    "socks5://41.242.69.196:5678",
    "socks5://38.51.48.18:5678",
    "socks5://187.188.169.169:59329",
    "socks5://74.119.147.209:4145",
    "socks5://24.249.199.4:4145",
    "socks5://51.94.6.53:3128",
    "socks5://89.109.179.51:1080",
    "socks5://41.216.232.213:4153",
    "socks5://178.220.148.82:10801",
    "socks5://141.94.70.195:46797",
    "socks5://36.94.110.49:5678",
    "socks5://94.230.127.180:1080",
    "socks5://170.106.151.187:42576"
]

# Get a random proxy from the list
import random
def get_random_proxy():
    return random.choice(PROXY_LIST) if PROXY_LIST else None

# Configure Chrome options
def setup_driver(use_proxy=True):
    chrome_options = Options()
    if use_proxy and PROXY_LIST:
        selected_proxy = get_random_proxy()
        print(f"Setting up Chrome with proxy: {selected_proxy}")
        chrome_options.add_argument(f'--proxy-server={selected_proxy}')
    else:
        print("Setting up Chrome without proxy")
    chrome_options.add_argument("--headless")  # Optional: remove if you want to see the browser
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # User agent to mimic a real browser
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    return webdriver.Chrome(options=chrome_options)

# Define categories and search queries
categories = {
    "men": "Sri Lankan men",
    "women": "Sri Lankan women",
    "children": "Sri Lankan children"
}

def scroll_and_collect_images(driver, scroll_count=5):
    """Scroll down the page and collect image thumbnails"""
    print("Scrolling and collecting images...")
    
    # Initial thumbnails to compare
    previous_count = 0
    
    for i in range(scroll_count):
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)  # Wait for page to load new images
        
        # Get current thumbnails
        thumbnails = driver.find_elements(By.CSS_SELECTOR, "img.rg_i")
        current_count = len(thumbnails)
        
        print(f"Scroll {i+1}/{scroll_count} - Found {current_count} images")
        
        # If no new images are loading, break early
        if current_count == previous_count:
            if i >= 2:  # After at least 3 scrolls
                print("No new images loading, stopping scroll")
                break
        
        previous_count = current_count
    
    # Collect all thumbnails after scrolling
    thumbnails = driver.find_elements(By.CSS_SELECTOR, "img.rg_i")
    print(f"Total thumbnails found: {len(thumbnails)}")
    return thumbnails

def download_image(url, save_path, index, use_proxy=False):
    """Download image from URL and save to specified path"""
    try:
        # For data URLs (base64 encoded images)
        if url.startswith('data:image'):
            header, encoded = url.split(",", 1)
            data = base64.b64decode(encoded)
            ext = header.split(";")[0].split("/")[-1]
            if not ext or ext == "octet-stream":
                ext = "jpg"  # Default extension
        # For regular URLs
        else:
            # Add random delay to avoid being detected as a bot
            time.sleep(random.uniform(0.1, 0.5))
            
            # Get image data with headers to mimic a browser
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com/"
            }
            
            # Configure proxy for requests if needed
            proxies = None
            if use_proxy and PROXY_LIST:
                # Try with a random proxy from the list
                selected_proxy = get_random_proxy()
                
                if selected_proxy.startswith("socks"):
                    proxies = {
                        "http": selected_proxy,
                        "https": selected_proxy
                    }
                elif selected_proxy.startswith("http"):
                    proxies = {
                        "http": selected_proxy,
                        "https": selected_proxy
                    }
            
            # First try with proxy if enabled
            try:
                if proxies:
                    print(f"Downloading with proxy {selected_proxy}: {url[:40]}...")
                    response = requests.get(url, headers=headers, timeout=15, proxies=proxies)
                else:
                    print(f"Downloading direct: {url[:40]}...")
                    response = requests.get(url, headers=headers, timeout=10)
                
                # Check if the response was successful
                if response.status_code != 200:
                    print(f"Failed to download image, status code: {response.status_code}")
                    # If proxy fails, try without proxy as fallback
                    if proxies:
                        print("Trying without proxy...")
                        response = requests.get(url, headers=headers, timeout=10)
                        if response.status_code != 200:
                            print(f"Direct download also failed, status code: {response.status_code}")
                            return False
                        print("Direct download successful")
                    else:
                        return False
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")
                # Try without proxy if there was an error
                if proxies:
                    print("Proxy error, trying direct download...")
                    try:
                        response = requests.get(url, headers=headers, timeout=10)
                        if response.status_code != 200:
                            print(f"Direct download failed, status code: {response.status_code}")
                            return False
                        print("Direct download successful")
                    except requests.exceptions.RequestException as e2:
                        print(f"Direct download also failed: {e2}")
                        return False
                else:
                    return False
            
            data = response.content
            
            # Try to get extension from URL or content type
            content_type = response.headers.get('Content-Type', '')
            if 'image/' in content_type:
                ext = content_type.split('/')[-1]
            else:
                ext = os.path.splitext(urlparse(url).path)[-1][1:] or "jpg"
                
        # Clean up extension
        ext = ext.lower().split(';')[0].split('+')[0]
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
            ext = "jpg"
            
        # Create filename with index to ensure order and uniqueness
        filename = f"{index:03d}_{int(time.time())}.{ext}"
        filepath = os.path.join(save_path, filename)
        
        # Save image
        with open(filepath, 'wb') as f:
            f.write(data)
        
        print(f"Successfully downloaded: {filename}")
        return True
        
    except Exception as e:
        print(f"Failed to download image: {e}")
        return False

def test_proxy_connection(proxy):
    """Test if proxy is working by making a request to a test site"""
    try:
        print(f"\nTesting proxy connection to: {proxy}")
        # Set up a simple Chrome driver with the proxy
        chrome_options = Options()
        chrome_options.add_argument(f'--proxy-server={proxy}')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        test_driver = webdriver.Chrome(options=chrome_options)
        test_driver.set_page_load_timeout(30)  # Set timeout to 30 seconds
        
        # Try to access a test URL
        test_driver.get("https://httpbin.org/ip")
        
        # If we get here without an exception, the proxy is working
        try:
            page_source = test_driver.page_source
            print("Proxy test result:")
            print(page_source[:500])  # Print first 500 chars of response
        except Exception as e:
            print(f"Error reading proxy test result: {e}")
        
        test_driver.quit()
        return True
    except Exception as e:
        print(f"❌ Proxy test failed: {e}")
        return False

def test_proxy_list(proxy_list, max_tests=5):
    """Test multiple proxies from the list and return working ones"""
    working_proxies = []
    
    # Test a random sample of proxies
    test_proxies = random.sample(proxy_list, min(max_tests, len(proxy_list)))
    
    for proxy in test_proxies:
        if test_proxy_connection(proxy):
            working_proxies.append(proxy)
            if len(working_proxies) >= 3:  # Once we have 3 working proxies, that's enough
                break
    
    return working_proxies

def main():
    # Create main directory for all images
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sri_lankan_images")
    os.makedirs(base_dir, exist_ok=True)
    
    # Using proxy list
    use_proxy = True
    print(f"Found {len(PROXY_LIST)} proxies to try")
    
    # Test proxies from the list
    print("Testing a sample of proxies to find working ones...")
    working_proxies = test_proxy_list(PROXY_LIST)
    
    if working_proxies:
        print(f"\n✅ Found {len(working_proxies)} working proxies")
        # Filter the main proxy list to prioritize working ones
        # Put working proxies at the beginning of the list
        for proxy in working_proxies:
            if proxy in PROXY_LIST:
                PROXY_LIST.remove(proxy)
            PROXY_LIST.insert(0, proxy)
    else:
        print("\n⚠️ No working proxies found in the sample test.")
        print("Continuing without proxy as free proxies often don't work reliably.")
        use_proxy = False
    
    # Create driver with fallback
    try:
        driver = setup_driver(use_proxy=use_proxy)
    except Exception as e:
        print(f"Error creating driver: {e}")
        print("Trying without proxy...")
        use_proxy = False
        driver = setup_driver(use_proxy=use_proxy)
    
    try:
        # Scrape each category
        for category, query in categories.items():
            print(f"\n{'='*50}")
            print(f"Scraping images for: {query}")
            print(f"{'='*50}")
            
            # Create category folder
            folder = os.path.join(base_dir, category)
            os.makedirs(folder, exist_ok=True)
            
            # Navigate to Google Images
            driver.get("https://www.google.com/imghp")
              # Wait for search box and enter query
            try:
                print("Waiting for search box to load...")
                search_box = WebDriverWait(driver, 20).until(  # Increased timeout
                    EC.presence_of_element_located((By.NAME, "q"))
                )
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.RETURN)
                
                # Wait for search results
                print("Searching for images... (waiting for results)")
                WebDriverWait(driver, 20).until(  # Increased timeout
                    EC.presence_of_element_located((By.CSS_SELECTOR, "img.rg_i"))
                )
            except Exception as e:
                print(f"Error searching for {query}: {e}")
                print("Taking screenshot for debugging...")
                try:
                    screenshot_path = os.path.join(base_dir, f"error_{category}.png")
                    driver.save_screenshot(screenshot_path)
                    print(f"Screenshot saved to: {screenshot_path}")
                    print(f"Current page title: {driver.title}")
                    print(f"Current URL: {driver.current_url}")
                except Exception as ss_err:
                    print(f"Failed to save screenshot: {ss_err}")
                continue
                
            # Collect image thumbnails
            thumbnails = scroll_and_collect_images(driver, scroll_count=8)
            
            print(f"\n[{category}] Found {len(thumbnails)} thumbnails. Starting download...")
            
            # Process each thumbnail
            successful_downloads = 0
            max_images = 50  # Maximum images to download per category
            
            for i, thumb in enumerate(thumbnails):
                if successful_downloads >= max_images:
                    break
                    
                try:
                    # Get image URL
                    # First try to get the source directly
                    image_url = None
                    
                    # Click thumbnail to open larger image
                    driver.execute_script("arguments[0].click();", thumb)
                    time.sleep(1)  # Wait for larger image to load
                    
                    try:
                        # Wait for the large image container
                        large_img = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "img.n3VNCb, img.r48jcc"))
                        )
                        
                        # Try to get the source from multiple attributes
                        image_url = large_img.get_attribute("src")
                        
                        # Make sure it's a valid image URL
                        if not image_url or (not image_url.startswith('http') and not image_url.startswith('data:image')):
                            # Try alternate attribute
                            image_url = large_img.get_attribute("data-src")
                    
                    except Exception as e:
                        print(f"Error getting image URL: {e}")
                        continue
                          # If we have a valid URL, download the image
                    if image_url and (image_url.startswith('http') or image_url.startswith('data:image')):
                        if download_image(image_url, folder, i, use_proxy=use_proxy):
                            successful_downloads += 1
                            print(f"Progress: {successful_downloads}/{max_images}")
                    
                except Exception as e:
                    print(f"Error processing thumbnail: {e}")
                    
                # Add random delay between downloads
                time.sleep(random.uniform(0.5, 2.0))
                
            print(f"\nCompleted {category}: Downloaded {successful_downloads} images")
            
            # If regular approach failed or found very few images, try direct download
            if successful_downloads < 10:
                print(f"\nFew images downloaded using browser method. Trying direct download for {query}...")
                try:
                    direct_download_images(query, folder, max_images - successful_downloads, use_proxy)
                except Exception as e:
                    print(f"Direct download failed: {e}")
    
    finally:
        # Clean up
        print("\nScraping completed. Closing browser...")
        driver.quit()

def direct_download_images(query, save_folder, max_images=20, use_proxy=False):
    """Alternative approach to download images directly from Google Images API"""
    print(f"Attempting direct download for: {query}")
    
    # Encode the search query
    search_query = query.replace(' ', '+')
    
    # Set up the request headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }
      # Configure proxy if needed
    proxies = None
    if use_proxy and PROXY_LIST:
        # Try with a random proxy from the list
        selected_proxy = get_random_proxy()
        
        if selected_proxy.startswith("socks") or selected_proxy.startswith("http"):
            proxies = {
                "http": selected_proxy,
                "https": selected_proxy
            }
    
    # Try a few different Google Images URLs/formats
    urls = [
        f"https://www.google.com/search?q={search_query}&tbm=isch&safe=active",
        f"https://www.google.com/search?q={search_query}&source=lnms&tbm=isch"
    ]
    
    downloaded = 0
    
    for url in urls:
        if downloaded >= max_images:
            break
            
        try:
            # Get the search results page
            print(f"Fetching: {url}")
            
            if proxies:
                response = requests.get(url, headers=headers, proxies=proxies, timeout=20)
            else:
                response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code != 200:
                print(f"Failed to fetch search results, status code: {response.status_code}")
                continue
                
            # Extract image URLs from the page source
            content = response.text
            
            # Very basic extraction - look for image URLs in the page source
            # This is not as reliable as using a browser, but can work as a fallback
            import re
            
            # Look for image URLs in the HTML
            image_urls = []
            
            # Pattern to match image URLs in the HTML source
            patterns = [
                r'https://encrypted-tbn0\.gstatic\.com/images\?[^"\']+',
                r'https://[^"\']*\.(?:jpg|jpeg|png|gif|bmp|webp)[^"\'\s]*',
                r'"ou":"(https://[^"]+)"'
            ]
            
            for pattern in patterns:
                if re.compile(pattern).search(content):
                    matches = re.findall(pattern, content)
                    image_urls.extend(matches)
            
            print(f"Found {len(image_urls)} potential image URLs")
            
            # Download each image
            for i, img_url in enumerate(image_urls):
                if downloaded >= max_images:
                    break
                
                # Clean up URL if it's from a JSON structure
                if img_url.startswith('"ou":"'):
                    img_url = img_url.replace('"ou":"', '')
                
                # Fix escaped URLs
                img_url = img_url.replace('\\u003d', '=').replace('\\u0026', '&')
                
                try:
                    if download_image(img_url, save_folder, i + 1000, use_proxy=use_proxy):
                        downloaded += 1
                        print(f"Direct download progress: {downloaded}/{max_images}")
                except Exception as e:
                    print(f"Error downloading image {i}: {e}")
                
                # Add delay
                time.sleep(random.uniform(0.5, 1.5))
                
        except Exception as e:
            print(f"Error in direct download: {e}")
    
    return downloaded

if __name__ == "__main__":
    main()
