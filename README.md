# Web Resource Downloader

A Python script designed to download a webpage's HTML content and its associated resources (images, scripts, and stylesheets) to a local directory, with a focus on simplicity and efficiency.

---

## ✨ Features

- Downloads webpage HTML and linked resources (images, scripts, stylesheets)
- Organizes files into structured subdirectories (`html`, `img`, `script`, `stylesheet`)
- Supports concurrent downloads with a visual progress bar
- Logs operations to both console and a `scraper.log` file
- Provides command-line argument flexibility
- Includes robust error handling and URL validation
- Automatically handles duplicate filenames

---

## 🧰 Prerequisites

- Python 3.6 or higher
- Required Python packages:

  ```bash
  pip install requests beautifulsoup4 tqdm
  ```

---

## 🛠️ Installation

1. Clone or download this repository to your local machine.
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   Alternatively, install the packages manually:

   ```bash
   pip install requests beautifulsoup4 tqdm
   ```

---

## 🚀 Usage

Run the script from the command line using the following syntax:

```bash
python web_scraper.py <URL> [-o OUTPUT_FOLDER] [-w WORKERS]
```

### Arguments

- `URL`: The webpage URL to download (required).
- `-o, --output`: Specifies the output folder path (default: `downloaded_files`).
- `-w, --workers`: Sets the number of concurrent download threads (default: 4).

### Example

```bash
python web_scraper.py https://example.com -o my_downloads -w 8
```

This command will:

- Download the webpage from `https://example.com`
- Save all files to the `my_downloads` folder
- Use 8 concurrent download threads
- Create subdirectories: `html`, `img`, `script`, `stylesheet`
- Display a progress bar during the download process
- Log all operations to both the console and `scraper.log`

---

## 📂 Output Structure

The downloaded files are organized as follows:

```
my_downloads/
├── html/
│   └── index.html
├── img/
│   └── [image files]
├── script/
│   └── [javascript files]
├── stylesheet/
│   └── [css files]
└── scraper.log
```

---

## 📝 Notes

- Invalid or unreachable URLs are skipped, with errors logged for review.
- Duplicate filenames are automatically renamed to avoid conflicts.
- Large files are downloaded in chunks to optimize memory usage.
- Logs are stored in `scraper.log` for debugging and tracking.
- The script currently supports only `img`, `script`, and `stylesheet` resources; other resource types are ignored.

---

## 🧪 Troubleshooting

- Verify that the provided URL is accessible and properly formatted.
- Review `scraper.log` for detailed error messages if issues arise.
- Ensure you have write permissions in the specified output directory.
- Confirm that all required dependencies are installed correctly.

---

## 📄 License

This project is licensed under the MIT License.
