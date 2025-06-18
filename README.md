Here is the updated `README.md` file content with the **free SOCKS proxy integration** included for your Sri Lankan Image Downloader project. The new section clearly documents proxy usage with a note on its dynamic update source.

---

````markdown
# 🇱🇰 Sri Lankan Image Downloader

This project is designed to download high-quality images of Sri Lankan people across various professional and demographic categories using web scraping techniques.

---

## 📦 Installation Requirements

To get started, install the required Python packages:

```bash
pip install requests beautifulsoup4 pillow selenium webdriver-manager
````

Alternatively, install all dependencies at once:

```bash
pip install -r requirements.txt
```

---

## ⚙️ How the Project Works

The project includes Python scripts that scrape image search engines (primarily Bing, optionally Google and others), and save images to structured folders based on professions and demographics.

### Key Scripts

| Script                                | Description                                                         |
| ------------------------------------- | ------------------------------------------------------------------- |
| `simplified_downloader.py`            | Basic image downloader for men, women, and children.                |
| `professional_downloader.py`          | Downloads categorized professional images (e.g. doctors, teachers). |
| `enhanced_professional_downloader.py` | Uses smarter queries for better accuracy and variety.               |
| `direct_image_downloader.py`          | Multi-source continuous downloader (Bing, Unsplash, etc.).          |
| `google_image_scraper.py`             | Selenium-based scraper for Google Images.                           |

---

## 🧑‍💻 How to Use

### ✅ Option 1: Interactive

Run the batch file or terminal script:

```bash
pip install -r requirements.txt
```

Follow on-screen prompts to choose a scraping module.

### ⚡ Option 2: Direct Run

Example:

```bash
python enhanced_professional_downloader.py
```

### 🎯 Option 3: Specify Categories

Example:

```bash
python professional_downloader.py healthcare teachers
```

---

## 📁 Output Directory

All downloaded images are saved in:

```bash
sri_lankan_images/
```

Images are automatically organized into subfolders by category.

---

## 🌐 Proxy Support

To improve anonymity and avoid IP blocks, this project supports the use of SOCKS proxies. A list of updated proxies is pulled from:

**[https://www.socks-proxy.net](https://www.socks-proxy.net)**

Latest update timestamp (as of this README):
**2025-06-17 08:42:02 UTC**

Example proxy (format: `IP:PORT`):

```
18.203.249.67:10010
184.178.172.11:4145
103.144.18.95:80
...
```

> 💡 You can modify the `proxy_list.txt` or integrate dynamic fetching in the script to use these automatically.

Use with Python scripts (basic example in code):

```python
proxies = {
    'http': 'socks5h://18.203.249.67:10010',
    'https': 'socks5h://18.203.249.67:10010'
}
response = requests.get('https://www.bing.com/images', proxies=proxies)
```

---

## 🌟 Key Features

* ✅ High-resolution image downloading
* 🗂️ Professionally categorized folders
* 🔍 Smart search query optimization
* 🕵️ Anti-bot techniques (random delays, user-agent spoofing)
* 🌐 Supports multiple image sources: Bing, Google, Unsplash
* 🔁 Continuous scraping mode
* 🧰 SOCKS proxy support for anonymity

---

## ⚠️ Disclaimer

This project is intended for **educational and research** purposes only. Always respect copyright and licensing laws when downloading and using images.

---

## 🤝 Contributing

Pull requests are welcome. For significant changes, please open an issue first to discuss what you'd like to improve or expand.



```

---

Let me know if you’d like this as an actual downloadable `.md` file or if you want me to help automate the proxy fetching into your script.
```
