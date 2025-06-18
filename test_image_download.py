import requests
import os
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote_plus

print("Testing image downloader functionality...")
# Create test directory
os.makedirs("test_images", exist_ok=True)

# Try to download from Bing
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
headers = {
    "User-Agent": user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

# Test Bing search
print("Testing Bing search...")
query = "Sri Lankan men"
search_url = f"https://www.bing.com/images/search?q={quote_plus(query)}&form=HDRSC2&first=1"

try:
    response = requests.get(search_url, headers=headers, timeout=20)
    print(f"Bing response status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Page title: {soup.title.text if soup.title else 'No title'}")
        
        # Find image links
        image_urls = []
        # Look for murl attributes which contain full-size image URLs
        for link in soup.find_all('a', {'class': 'iusc'}):
            try:
                m = link.get('m', '')
                if m:
                    # This contains JSON with the full image URL
                    import json
                    try:
                        m_data = json.loads(m)
                        if 'murl' in m_data:
                            full_img_url = m_data['murl']
                            if full_img_url and 'http' in full_img_url:
                                image_urls.append(full_img_url)
                    except:
                        pass
            except Exception as e:
                print(f"Error parsing link: {e}")
        
        print(f"Found {len(image_urls)} image URLs from Bing")
        
        # Try to download a few images
        for i, url in enumerate(image_urls[:3]):  # Test first 3 images
            print(f"Downloading image {i+1}: {url[:100]}...")
            try:
                img_response = requests.get(url, headers={"User-Agent": user_agent}, timeout=15)
                if img_response.status_code == 200:
                    # Get file extension
                    content_type = img_response.headers.get('Content-Type', '')
                    if 'image/' in content_type:
                        ext = content_type.split('/')[-1]
                    else:
                        ext = os.path.splitext(urlparse(url).path)[-1][1:] or "jpg"
                    
                    # Clean extension
                    ext = ext.lower().split(';')[0].split('+')[0]
                    if ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                        ext = "jpg"
                    
                    # Save image
                    filepath = os.path.join("test_images", f"test_image_{i+1}.{ext}")
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    
                    # Check file size
                    file_size = os.path.getsize(filepath)
                    print(f"Downloaded image: {filepath} ({file_size/1024:.1f}KB)")
                else:
                    print(f"Failed to download image: HTTP {img_response.status_code}")
            except Exception as e:
                print(f"Error downloading image: {e}")
    
    # Try other sources like Unsplash
    print("\nTesting Unsplash...")
    unsplash_url = f"https://unsplash.com/s/photos/{query.replace(' ', '-')}"
    response = requests.get(unsplash_url, headers=headers, timeout=15)
    print(f"Unsplash response status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Page title: {soup.title.text if soup.title else 'No title'}")
        
        # Find image elements
        image_urls = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and 'https://images.unsplash.com' in src:
                image_urls.append(src)
        
        print(f"Found {len(image_urls)} image URLs from Unsplash")

except Exception as e:
    print(f"Error during test: {e}")

print("Test completed.")
