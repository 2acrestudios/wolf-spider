import os
import requests
from bs4 import BeautifulSoup
import pdfkit
from urllib.parse import urljoin, urlparse, urldefrag
from tqdm import tqdm

class WebsiteCrawler:
    def __init__(self, root_url):
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

    def fetch_page(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def get_pdf_filename(self, url):
        parsed_url = urlparse(url)
        path = parsed_url.path.strip("/").replace("/", "_")
        if not path:
            path = "index"
        return os.path.join(self.output_dir, f"{path}.pdf")

    def save_page_as_pdf(self, url):
        filename = self.get_pdf_filename(url)
        if os.path.exists(filename):
            print(f"PDF already exists for {url}, skipping.")
            return
        print(f"Saving {url} as {filename}")
        pdfkit.from_url(url, filename, options=self.pdf_options)

    def crawl(self):
        with tqdm(total=len(self.to_visit_links), bar_format='{l_bar}🕷️|{bar}| {n_fmt}/{total_fmt} [elapsed: {elapsed} remaining: {remaining}]') as pbar:
            while self.to_visit_links:
                current_url = self.to_visit_links.pop()
                if current_url in self.visited_links:
                    pbar.update(1)
                    continue

                print(f"Visiting: {current_url}")
                page_content = self.fetch_page(current_url)
                if page_content is None:
                    pbar.update(1)
                    continue

                self.visited_links.add(current_url)
                self.save_page_as_pdf(current_url)
                self.find_links_on_page(current_url, page_content)
                pbar.total = len(self.to_visit_links) + len(self.visited_links)
                pbar.update(1)

    def find_links_on_page(self, base_url, page_content):
        soup = BeautifulSoup(page_content, 'html.parser')
        for link in soup.find_all('a', href=True):
            url = urljoin(base_url, link['href'])
            url, _ = urldefrag(url)  # Remove anchor from URL
            if self.is_valid_url(url):
                if url not in self.visited_links and url not in self.to_visit_links:
                    self.to_visit_links.add(url)

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.scheme in {"http", "https"} and parsed_url.netloc == self.domain_name

if __name__ == "__main__":
    root_url = input("Enter the root URL: ")
    crawler = WebsiteCrawler(root_url)
    crawler.crawl()
