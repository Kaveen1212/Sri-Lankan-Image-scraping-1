import requests
import os
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlencode, quote_plus
import sys
import json

print("Direct Image Downloader for Sri Lankan People Categories")
print("=" * 60)
print("This script uses direct HTTP requests to download images (no Selenium required)")
print("Images will be downloaded in high quality (avoiding thumbnails)")
print("There is no download limit - script will keep finding images until stopped (Ctrl+C)")
print("=" * 60)
print()

# Create directories for each category
categories = {
    "men": "Sri Lankan men",
    "women": "Sri Lankan women",
    "children": "Sri Lankan children"
}

# Create base directory
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sri_lankan_images")
os.makedirs(base_dir, exist_ok=True)

# Create category directories
for category in categories:
    folder = os.path.join(base_dir, category)
    os.makedirs(folder, exist_ok=True)
    print(f"Created directory for {category}")

# User agent rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
]

def get_random_header():
    """Generate random headers to avoid detection"""
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }

def download_image(url, save_path, index):
    """Download high-quality image from URL and save it to the specified path"""
    try:
        # Add random delay
        time.sleep(random.uniform(0.5, 1.5))
        
        # Skip known thumbnail URLs before even downloading
        if any(x in url.lower() for x in ['thumb', 'icon', 'avatar', 'logo', 'button', '50x50', '100x100', 'icon_', '_icon', '_small']):
            print(f"Skipping likely thumbnail URL: {url[:100]}")
            return False
            
        # Request image with headers
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }
        
        print(f"Downloading: {url[:100]}...")
        
        try:
            response = requests.get(url, headers=headers, timeout=20, stream=True)
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            return False
        
        if response.status_code != 200:
            print(f"Failed to download image: Status {response.status_code}")
            return False
        
        # Check if image is high quality (min size)
        content_length = int(response.headers.get('Content-Length', 0))
        if content_length < 30000:  # Skip images smaller than 30KB - likely thumbnails
            print(f"Skipping small image ({content_length/1024:.1f}KB) - likely a thumbnail")
            return False
            
        # Determine file extension
        content_type = response.headers.get('Content-Type', '')
        if 'image/' in content_type:
            ext = content_type.split('/')[-1]
        else:
            ext = os.path.splitext(urlparse(url).path)[-1][1:] or "jpg"
        
        # Clean extension
        ext = ext.lower().split(';')[0].split('+')[0]
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
            ext = "jpg"
        
        # Generate descriptive filename with original URL encoded in the name
        # This helps avoid duplicates and track image sources
        url_hash = str(abs(hash(url)))[-8:]  # Use part of URL hash for filename
        filename = f"{index:03d}_{url_hash}_{int(time.time())}.{ext}"
        filepath = os.path.join(save_path, filename)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Verify file size after download
        file_size = os.path.getsize(filepath)
        if file_size < 20000:  # Check for tiny images after download
            print(f"Removing small image file: {filename} ({file_size/1024:.1f}KB)")
            os.remove(filepath)
            return False
        
        # Check image dimensions if possible (requires PIL/Pillow)
        try:
            from PIL import Image
            img = Image.open(filepath)
            width, height = img.size
            img.close()
            
            if width < 300 or height < 300:  # Skip images smaller than 300x300 pixels
                print(f"Removing low-resolution image: {filename} ({width}x{height}px)")
                os.remove(filepath)
                return False
                
            print(f"Downloaded high-quality image: {filename} ({width}x{height}px, {file_size/1024:.1f}KB)")
            
        except ImportError:
            print(f"Downloaded: {filename} ({file_size/1024:.1f}KB)")
        except Exception as e:
            print(f"Error checking image dimensions: {e}")
            print(f"Downloaded: {filename} ({file_size/1024:.1f}KB)")
            
        return True
        
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False

def search_bing_images(query, max_results=35):
    """Search Bing Images for high-quality images"""
    print(f"Searching Bing Images for: {query}")
    image_urls = set()
    
    try:
        # Try multiple pages
        for page_num in range(0, 3):  # Get first 3 pages of results
            offset = 1 + (page_num * 35)
            search_url = f"https://www.bing.com/images/search?q={quote_plus(query)}&form=HDRSC2&first={offset}"
            
            headers = get_random_header()
            print(f"  Requesting Bing page {page_num+1}...")
            response = requests.get(search_url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                print(f"  Got successful response from Bing (page {page_num+1})")
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for murl attributes which contain full-size image URLs
                for link in soup.find_all('a', {'class': 'iusc'}):
                    try:
                        m = link.get('m', '')
                        if m:
                            # This contains JSON with the full image URL
                            try:
                                m_data = json.loads(m)
                                if 'murl' in m_data:
                                    full_img_url = m_data['murl']
                                    if full_img_url and 'http' in full_img_url:
                                        image_urls.add(full_img_url)
                            except:
                                pass
                    except:
                        pass
                
                print(f"  Found {len(image_urls)} images from Bing so far")
                
                # Add delay between pages
                time.sleep(random.uniform(1.0, 2.0))
            else:
                print(f"  Bing search failed for page {page_num+1}: Status {response.status_code}")
                break
        
    except Exception as e:
        print(f"Error during Bing search: {e}")
    
    return list(image_urls)

def main():
    total_downloaded = 0
    
    print(f"\nStarting unlimited high-quality image download for Sri Lankan people categories...")
    print(f"Press Ctrl+C to stop the script at any time")
    
    for category, query in categories.items():
        print(f"\n{'='*50}")
        print(f"Processing category: {category} - Search query: {query}")
        print(f"{'='*50}")
        
        # Get folder path
        folder = os.path.join(base_dir, category)
        
        # Get images from Bing - our most reliable source
        image_urls = search_bing_images(query)
        
        # Download images
        print(f"\nFound {len(image_urls)} potential image URLs for {category}")
        downloaded = 0
        
        for i, url in enumerate(image_urls):
            if download_image(url, folder, downloaded+1):
                downloaded += 1
                print(f"Progress: {downloaded} images downloaded for {category}")
            
            # Add tiny delay between downloads
            time.sleep(random.uniform(0.1, 0.3))
        
        print(f"\nCompleted {category}: Downloaded {downloaded} images")
        total_downloaded += downloaded
        
    print(f"\nTotal images downloaded: {total_downloaded}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)
