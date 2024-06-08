import os
import requests
from bs4 import BeautifulSoup
import pdfkit
from urllib.parse import urljoin, urlparse, urldefrag
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

class WebsiteCrawler:
    """
    A class to crawl a website and convert its pages into PDF files.

    Attributes:
        root_url (str): The root URL of the website to crawl.
        visited_links (set): A set of URLs that have already been visited.
        to_visit_links (set): A set of URLs to be visited.
        pdf_options (dict): Options for PDF conversion.
        domain_name (str): The domain name of the root URL.
        output_dir (str): The directory where PDF files will be saved.

    Methods:
        fetch_page(url): Fetches the content of a given URL.
        get_pdf_filename(url): Generates a PDF filename for a given URL.
        save_page_as_pdf(url): Saves the content of a given URL as a PDF file.
        crawl(): Starts the crawling process.
        find_links_on_page(base_url, page_content): Finds and processes links on a given page.
        is_valid_url(url): Checks if a URL is valid and belongs to the same domain.
    """

    def __init__(self, root_url):
        """
        Initializes the WebsiteCrawler with a root URL.

        Args:
            root_url (str): The root URL to start crawling from.
        """
        self.root_url = root_url
        self.visited_links = set()
        self.to_visit_links = set([root_url])
        self.pdf_options = {
            'quiet': '',
            'enable-local-file-access': ''
        }
        self.domain_name = urlparse(root_url).netloc
        self.output_dir = self.domain_name

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Initialize Selenium WebDriver with headless option
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def __del__(self):
        self.driver.quit()

    def fetch_page(self, url):
        """
        Fetches the content of a given URL.

        Args:
            url (str): The URL to fetch.

        Returns:
            str: The content of the page if the request is successful, None otherwise.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def fetch_page_selenium(self, url):
        """
        Fetches the content of a given URL using Selenium.

        Args:
            url (str): The URL to fetch.

        Returns:
            str: The content of the page if the request is successful, None otherwise.
        """
        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for JavaScript to load content
            return self.driver.page_source
        except Exception as e:
            print(f"Failed to fetch {url} with Selenium: {e}")
            return None

    def get_pdf_filename(self, url):
        """
        Generates a PDF filename for a given URL.

        Args:
            url (str): The URL to generate a filename for.

        Returns:
            str: The generated PDF filename.
        """
        parsed_url = urlparse(url)
        path = parsed_url.path.strip("/").replace("/", "_")
        if not path:
            path = "index"
        return os.path.join(self.output_dir, f"{path}.pdf")

    def save_page_as_pdf(self, url):
        """
        Saves the content of a given URL as a PDF file.

        Args:
            url (str): The URL to save as PDF.
        """
        filename = self.get_pdf_filename(url)
        if os.path.exists(filename):
            print(f"PDF already exists for {url}, skipping.")
            return
        print(f"Saving {url} as {filename}")
        try:
            pdfkit.from_url(url, filename, options=self.pdf_options)
        except IOError as e:
            print(f"Failed to convert {url} to PDF: {e}")

    def crawl(self):
        """
        Starts the crawling process.
        """
        with tqdm(total=len(self.to_visit_links), bar_format='{l_bar}🕷️|{bar}| {n_fmt}/{total_fmt} [elapsed: {elapsed} remaining: {remaining}]') as pbar:
            while self.to_visit_links:
                current_url = self.to_visit_links.pop()
                if current_url in self.visited_links:
                    pbar.update(1)
                    continue

                print(f"Visiting: {current_url}")
                page_content = self.fetch_page(current_url)
                if page_content is None:
                    page_content = self.fetch_page_selenium(current_url)

                if page_content is None:
                    pbar.update(1)
                    continue

                self.visited_links.add(current_url)
                try:
                    self.save_page_as_pdf(current_url)
                except Exception as e:
                    print(f"An error occurred while saving PDF for {current_url}: {e}")
                self.find_links_on_page(current_url, page_content)
                pbar.total = len(self.to_visit_links) + len(self.visited_links)
                pbar.update(1)

    def find_links_on_page(self, base_url, page_content):
        """
        Finds and processes links on a given page.

        Args:
            base_url (str): The base URL of the page.
            page_content (str): The content of the page.
        """
        soup = BeautifulSoup(page_content, 'html.parser')
        for link in soup.find_all('a', href=True):
            url = urljoin(base_url, link['href'])
            url, _ = urldefrag(url)  # Remove anchor from URL
            if self.is_valid_url(url):
                if url not in self.visited_links and url not in self.to_visit_links:
                    self.to_visit_links.add(url)

    def is_valid_url(self, url):
        """
        Checks if a URL is valid and belongs to the same domain.

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL is valid and belongs to the same domain, False otherwise.
        """
        parsed_url = urlparse(url)
        return parsed_url.scheme in {"http", "https"} and parsed_url.netloc == self.domain_name

if __name__ == "__main__":
    root_url = input("Enter the root URL: ")
    crawler = WebsiteCrawler(root_url)
    crawler.crawl()
