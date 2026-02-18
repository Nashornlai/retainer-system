import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin, urlparse

class WebsiteWalker:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    def clean_url(self, url):
        """Ensures URL starts with http/https."""
        if not url.startswith("http"):
            return "https://" + url
        return url

    def find_email(self, url):
        """
        Crawls the homepage and common subpages (Contact, Impressum) for emails.
        Returns the first email found or None.
        """
        url = self.clean_url(url)
        print(f"🕷️ Crawling {url}...")
        
        # 1. Check Homepage
        email = self._scan_page(url)
        if email: return email

        # 2. Find "Contact" or "Impressum" links
        subpages = self._find_contact_links(url)
        
        # 3. Scan Subpages
        for link in subpages:
            time.sleep(1) # Be polite
            email = self._scan_page(link)
            if email: return email
            
        return None

    def _scan_page(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return None
            
            # Search in Mailto links first (High confidence)
            soup = BeautifulSoup(response.text, 'html.parser')
            mailto = soup.select_one("a[href^='mailto:']")
            if mailto:
                return mailto['href'].replace("mailto:", "").split("?")[0].strip()

            # Search in text (Regex)
            text = soup.get_text()
            match = re.search(self.email_regex, text)
            if match:
                return match.group(0)
            
        except Exception as e:
            print(f"⚠️ Error crawling {url}: {e}")
        return None

    def _find_contact_links(self, base_url):
        """Finds links to likely contact pages."""
        likely_pages = []
        try:
            response = requests.get(base_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            keywords = ["contact", "kontakt", "impressum", "about", "über uns"]
            
            for a in soup.find_all("a", href=True):
                href = a['href']
                text = a.get_text().lower()
                
                # Check if keyword in text or URL
                if any(k in text or k in href.lower() for k in keywords):
                    full_url = urljoin(base_url, href)
                    if urlparse(full_url).netloc == urlparse(base_url).netloc: # Internal links only
                        likely_pages.append(full_url)
                        
        except Exception:
            pass
        
        return list(set(likely_pages))[:3] # Limit to 3 pages

if __name__ == "__main__":
    walker = WebsiteWalker()
    # Test on a safe site or example
    print(walker.find_email("https://www.example.com"))
