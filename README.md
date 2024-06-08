# Wolf Spider - Web Page to PDF Converter

<img src="https://2acrestudios.com/wp-content/uploads/2024/06/00015-2283926452.png" style="width: 300px;" align="right" />

Wolf Spider is a Python script that crawls a website and converts its pages into PDFs. It is designed to handle a whole website, starting from a root URL, and create PDF files for each page it visits.

**Features**
- Crawls web pages starting from a root URL.
- Converts each web page to a PDF file.
- Handles local file access for PDF generation.
- Uses progress bar to indicate the crawling process.

**Installation**

1. Clone the repository:
    ```bash
    git clone https://github.com/marc-shade/wolf-spider/wolf-spider.git
    cd wolf-spider
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Install `wkhtmltopdf` which `pdfkit` depends on:
    - On Ubuntu:
        ```bash
        sudo apt-get install wkhtmltopdf
        ```
    - On macOS:
        ```bash
        brew install wkhtmltopdf
        ```
    - On Windows, download and install from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html).

## Usage

1. Run the script and enter the root URL when prompted:
    ```bash
    python wolf_spider.py
    ```

2. The script will create a directory named after the domain of the root URL and save all PDF files inside this directory.

3. If there are any issues with fetching pages or converting them to PDF, the script will log these errors to the console.

## Example
```bash
python wolf_spider.py
Enter the root URL: https://example.com
```
