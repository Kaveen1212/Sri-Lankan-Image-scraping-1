import requests
import os
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlencode, quote_plus
import sys

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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
]

def get_random_header():
    """Generate random headers to avoid detection"""
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "TE": "Trailers",
    }

def download_image(url, save_path, index):
    """Download high-quality image from URL and save it to the specified path"""
    try:
        # Add random delay
        time.sleep(random.uniform(0.5, 1.5))
        
        # Request image with headers
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            "sec-ch-ua-mobile": "?0",
        }
        
        print(f"Downloading: {url[:100]}...")
        
        # Skip known thumbnail URLs before even downloading
        if any(x in url.lower() for x in ['thumb', 'icon', 'avatar', 'logo', 'button', '50x50', '100x100', 'icon_', '_icon', '_small']):
            print(f"Skipping likely thumbnail URL: {url[:100]}")
            return False
            
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
        if content_length < 30000:  # Increased minimum size to 30KB to better filter thumbnails
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
        if file_size < 20000:  # Increased check for tiny images after download
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

def search_images(query, max_images=float('inf')):
    """Search for images using multiple sources and return URLs with no limit"""
    print(f"\nSearching for: {query}")
    image_urls = set()
    
    # Method 1: Multiple Bing search pages for more results
    try:
        # Get results from multiple pages (1, 35, 69, 103, etc.)
        for page_num in range(0, 15):  # Increased to 15 pages for more results
            offset = 1 + (page_num * 35)
            search_url = f"https://www.bing.com/images/search?q={quote_plus(query)}&form=HDRSC2&first={offset}&qft=+filterui:imagesize-large"
            
            headers = get_random_header()
            response = requests.get(search_url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find high-quality image links
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
                                        image_urls.add(full_img_url)
                            except:
                                pass
                    except:
                        pass
                
                # Also collect image elements with high-res sources
                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    data_src = img.get('data-src', '')
                    
                    # Skip small images that are likely thumbnails
                    if 'w=' in src and 'h=' in src:
                        try:
                            # Extract width from src URL if possible
                            w_index = src.index('w=')
                            width_str = src[w_index+2:].split('&')[0]
                            width = int(width_str)
                            if width < 400:  # Skip anything under 400px wide - likely thumbnails
                                continue
                        except:
                            pass
                    
                    if src and 'http' in src and ('.jpg' in src.lower() or '.png' in src.lower() or '.jpeg' in src.lower()):
                        image_urls.add(src)
                        
                    if data_src and 'http' in data_src:
                        image_urls.add(data_src)
                
                print(f"Found {len(image_urls)} images on Bing (page {page_num+1})")
                
                # Add delay between pages
                time.sleep(random.uniform(1.0, 3.0))
            else:
                print(f"Bing search failed for page {page_num+1}: Status {response.status_code}")
                break
        
    except Exception as e:
        print(f"Error during Bing search: {e}")
    
    # Method 2: Unsplash search
    try:
        unsplash_url = f"https://unsplash.com/s/photos/{query.replace(' ', '-')}"

        headers = get_random_header()
        response = requests.get(unsplash_url, headers=headers, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find image elements
            for img in soup.find_all('img'):
                src = img.get('src', '')
                srcset = img.get('srcset', '')

                if src and 'https://images.unsplash.com' in src:
                    # Replace with higher resolution if possible
                    if '?w=' in src:
                        src = src.split('?')[0] + '?w=1600'  # Request larger image
                    image_urls.add(src)

                if srcset:
                    # Parse srcset to get the largest image
                    parts = srcset.split(',')
                    for part in parts:
                        if 'https://images.unsplash.com' in part:
                            url = part.strip().split(' ')[0]
                            image_urls.add(url)

            print(f"Found {len(image_urls)} images after adding Unsplash")
        else:
            print(f"Unsplash search failed: Status {response.status_code}")

    except Exception as e:
        print(f"Error during Unsplash search: {e}")
        
    # Method 3: Pexels search
    try:
        pexels_url = f"https://www.pexels.com/search/{query.replace(' ', '%20')}/"
        
        headers = get_random_header()
        response = requests.get(pexels_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find image elements
            for img in soup.find_all('img'):
                src = img.get('src', '')
                srcset = img.get('srcset', '')
                data_large = img.get('data-large-src', '')
                
                if src and ('https://images.pexels.com' in src or 'https://www.pexels.com' in src):
                    # Try to get full-size image
                    if '?auto=' in src:
                        src = src.split('?')[0] + '?auto=compress&cs=tinysrgb&dpr=2&h=1200&w=1600'
                    image_urls.add(src)
                
                if data_large:
                    image_urls.add(data_large)
                
                if srcset:
                    # Parse srcset to get the largest image
                    parts = srcset.split(',')
                    for part in parts:
                        if 'https://images.pexels.com' in part:
                            url = part.strip().split(' ')[0]
                            image_urls.add(url)
            
            print(f"Found {len(image_urls)} images after adding Pexels")
        else:
            print(f"Pexels search failed: Status {response.status_code}")
    
    except Exception as e:
        print(f"Error during Pexels search: {e}")
        
    # Method 4: DuckDuckGo search (often has different results than Bing)
    try:
        ddg_url = f"https://duckduckgo.com/?q={quote_plus(query)}&t=h_&iax=images&ia=images"
        
        headers = get_random_header()
        response = requests.get(ddg_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for image data in the page source
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'vqd=' in script.string:
                    try:
                        import re
                        vqd_match = re.search(r'vqd=\'(.*?)\'', script.string)
                        if vqd_match:
                            vqd = vqd_match.group(1)
                            
                            # Now we can fetch the image results
                            img_api_url = f"https://duckduckgo.com/i.js?q={quote_plus(query)}&vqd={vqd}"
                            img_response = requests.get(img_api_url, headers=headers, timeout=15)
                            
                            if img_response.status_code == 200:
                                try:
                                    import json
                                    results = json.loads(img_response.text)
                                    if 'results' in results:
                                        for result in results['results']:
                                            if 'image' in result:
                                                image_urls.add(result['image'])
                                            if 'thumbnail' in result and result['thumbnail'].startswith("http"):
                                                # Use thumbnail URL structure to build full image URL if possible
                                                img_url = result['thumbnail']
                                                if 'thumbnails' in img_url:
                                                    full_img_url = img_url.replace('thumbnails', 'images')
                                                    image_urls.add(full_img_url)
                                except json.JSONDecodeError:
                                    pass
                    except:
                        pass
            
            print(f"Found {len(image_urls)} images after adding DuckDuckGo")
        else:
            print(f"DuckDuckGo search failed: Status {response.status_code}")
    except Exception as e:
        print(f"Error during DuckDuckGo search: {e}")

    # Method 5: Flickr search (good for cultural photos)
    try:
        flickr_url = f"https://www.flickr.com/search/?text={quote_plus(query)}"
        
        headers = get_random_header()
        response = requests.get(flickr_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find image elements
            for img in soup.find_all('img'):
                src = img.get('src', '')
                data_src = img.get('data-src', '')
                
                # Skip tiny thumbnails
                if 'buddyicons' in src or 'spaceball.gif' in src:
                    continue
                
                # Convert to higher resolution if possible
                if src and 'live.staticflickr.com' in src:
                    # Sample URL: https://live.staticflickr.com/65535/52953501783_01de8cc2c7_m.jpg
                    # Replace _m.jpg with _b.jpg for larger size
                    if '_m.jpg' in src:
                        src = src.replace('_m.jpg', '_b.jpg')
                    if '_n.jpg' in src:
                        src = src.replace('_n.jpg', '_b.jpg')
                    if '_s.jpg' in src:
                        src = src.replace('_s.jpg', '_b.jpg')
                    if '_q.jpg' in src:
                        src = src.replace('_q.jpg', '_b.jpg')
                    if '_t.jpg' in src:
                        src = src.replace('_t.jpg', '_b.jpg')
                    image_urls.add(src)
                
                if data_src and 'live.staticflickr.com' in data_src:
                    # Same conversion for data-src
                    if '_m.jpg' in data_src:
                        data_src = data_src.replace('_m.jpg', '_b.jpg')
                    if '_n.jpg' in data_src:
                        data_src = data_src.replace('_n.jpg', '_b.jpg')
                    if '_s.jpg' in data_src:
                        data_src = data_src.replace('_s.jpg', '_b.jpg')
                    if '_q.jpg' in data_src:
                        data_src = data_src.replace('_q.jpg', '_b.jpg')
                    if '_t.jpg' in data_src:
                        data_src = data_src.replace('_t.jpg', '_b.jpg')
                    image_urls.add(data_src)
            
            print(f"Found {len(image_urls)} images after adding Flickr")
        else:
            print(f"Flickr search failed: Status {response.status_code}")
    except Exception as e:
        print(f"Error during Flickr search: {e}")
    
    # Method 6: Google Images search - direct approach
    try:
        # Using Google Images search with direct parameters
        # Note: This approach might be against Google's ToS, use cautiously
        for start in range(0, 100, 10):  # Get 10 pages of results
            google_url = f"https://www.google.com/search?q={quote_plus(query)}&tbm=isch&hl=en&tbs=isz:l&start={start}"
            
            headers = get_random_header()
            response = requests.get(google_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try to find image URLs in Google's format
                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    if src and src.startswith('http') and not src.startswith('https://www.google.com/'):
                        image_urls.add(src)
                    
                # Look for links that might contain image URLs
                for a in soup.find_all('a'):
                    href = a.get('href', '')
                    if '/imgres?imgurl=' in href:
                        try:
                            # Extract the actual image URL
                            img_url = href.split('/imgres?imgurl=')[1].split('&')[0]
                            from urllib.parse import unquote
                            img_url = unquote(img_url)
                            if img_url.startswith('http'):
                                image_urls.add(img_url)
                        except:
                            pass
            else:
                print(f"Google search failed for page {start//10+1}: Status {response.status_code}")
                break
            
            # Add delay between pages to avoid being blocked
            time.sleep(random.uniform(2.0, 4.0))
        
        print(f"Found {len(image_urls)} images after adding Google Images")
    except Exception as e:
        print(f"Error during Google search: {e}")
    
    # Final filtering to remove known thumbnail URLs
    filtered_urls = []
    for url in image_urls:
        # Skip URLs that are known to be thumbnails or icons
        if any(x in url.lower() for x in ['icon', 'thumb', 'avatar', 'favicon', 'logo', 'button', 'badge', 'emoji']):
            continue
        if any(x in url.lower() for x in ['50x50', '100x100', '150x150', 'icon_']):
            continue
        if url.lower().endswith('.svg') or url.lower().endswith('.gif'):  # Skip SVG icons and GIFs
            continue
        if url.lower().endswith('.webp') and 'thumb' in url.lower():  # Skip webp thumbnails
            continue
        filtered_urls.append(url)
    
    print(f"Final count after filtering: {len(filtered_urls)} high-quality image URLs")
    return filtered_urls

def main():
    total_downloaded = 0
    # No limit on maximum images per category
    
    print(f"Starting unlimited high-quality image download for Sri Lankan people categories...")
    print(f"Images will be filtered to ensure only high-quality images are saved")
    print(f"Press Ctrl+C to stop the script at any time")
    
    for category, query in categories.items():
        print(f"\n{'='*50}")
        print(f"Searching for {query} images")
        print(f"{'='*50}")
        
        # Get folder path
        folder = os.path.join(base_dir, category)
        
        # Get all possible image URLs - no limit
        image_urls = search_images(query)
        
        # Download images - no limit
        print(f"Found {len(image_urls)} potential image URLs for {category}")
        downloaded = 0
        
        # Add more search terms for variety
        extended_queries = [
            f"{query} portrait",
            f"{query} traditional",
            f"{query} modern",
            f"{query} culture",
            f"{query} fashion",
            f"{query} professional",
            f"{query} family",
            f"{query} candid",
            f"{query} smiling",
            f"{query} photography",
            f"{query} HD",
            f"{query} high resolution",
            f"{query} traditional dress",
            f"{query} face"
        ]
        
        # First download from the main query
        for i, url in enumerate(image_urls):
            if download_image(url, folder, downloaded+1):
                downloaded += 1
                print(f"Progress: {downloaded} images downloaded for {category}")
        
        print(f"Downloaded {downloaded} images for main query")
        
        # Then try extended queries for more images - unlimited downloading
        for ext_query in extended_queries:
            print(f"\nSearching for additional images: {ext_query}")
            
            # Get additional image URLs from extended query
            ext_urls = search_images(ext_query)
            print(f"Found {len(ext_urls)} additional potential image URLs")
            
            # Download additional images - no limit
            url_count = 0
            for url in ext_urls:
                url_count += 1
                if url in image_urls:  # Skip duplicates
                    continue
                
                # Track URLs we've seen to avoid duplicates
                image_urls.add(url)
                    
                if download_image(url, folder, downloaded+1):
                    downloaded += 1
                    print(f"Progress: {downloaded} images downloaded for {category}")
                
                # Add tiny delay between downloads
                time.sleep(random.uniform(0.1, 0.3))
                
                # Print progress periodically
                if url_count % 10 == 0:
                    print(f"Processed {url_count}/{len(ext_urls)} URLs from extended query")
            
            # Add some delay between queries
            time.sleep(random.uniform(2.0, 5.0))
                
        print(f"\nCompleted {category}: Downloaded {downloaded} images")
        total_downloaded += downloaded
        
        # This category is done, but there's no limit - we'll continue with the next category
        print(f"Continuing to the next category... (no download limit enforced)")
        
    print(f"\nTotal images downloaded: {total_downloaded}")
    print(f"\nImage downloading completed. You can press Ctrl+C to exit or let the script continue searching for more images.")
    
    # Optional: Continue with repeat searches for even more images
    print(f"\nContinuing to search for more images indefinitely...")
    
    try:
        # Infinite loop to keep searching for more images with varied queries
        while True:
            for category, query in categories.items():
                # Create diverse new search queries
                time_suffix = int(time.time()) % 1000  # Add timestamp for variety
                diverse_queries = [
                    f"{query} {time_suffix}",
                    f"authentic {query} photos",
                    f"real {query} portraits",
                    f"{query} daily life",
                    f"{query} community",
                    f"{query} close up",
                    f"{query} lifestyle"
                ]
                
                # Search with each diverse query
                for div_query in diverse_queries:
                    try:
                        print(f"\nContinuing search with: {div_query}")
                        folder = os.path.join(base_dir, category)
                        more_urls = search_images(div_query)
                        
                        # Count existing files in this category folder
                        existing_count = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
                        
                        # Download any new images found
                        new_downloaded = 0
                        for url in more_urls:
                            if download_image(url, folder, existing_count + new_downloaded + 1):
                                new_downloaded += 1
                                
                        print(f"Downloaded {new_downloaded} additional images for {category}")
                        total_downloaded += new_downloaded
                    except Exception as e:
                        print(f"Error in continuous search: {e}")
                        
                    # Add delay between queries
                    time.sleep(random.uniform(5.0, 10.0))
                    
            print(f"Completed another search cycle. Total downloaded so far: {total_downloaded}")
            print(f"Waiting before next search cycle...")
            time.sleep(60)  # Wait a minute between full search cycles
            
    except KeyboardInterrupt:
        print("\nContinuous search stopped by user.")
        print(f"Final total: {total_downloaded} images downloaded across all categories")
