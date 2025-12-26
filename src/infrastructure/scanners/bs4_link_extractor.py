import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag
from typing import List, Set
from src.core.ports import LinkExtractor


class Bs4LinkExtractor(LinkExtractor):
    """
    BeautifulSoup kullanarak sayfadaki tüm geçerli linkleri toplar.
    """

    def extract_links(self, url: str) -> List[str]:
        print(f"   🔍 LinkExtractor Çalışıyor: {url}")
        found_links: Set[str] = set()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                return []
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup.find_all("a", href=True):
                href = tag.get("href")

                href = href.strip()
                if not href:
                    continue

                if href.startswith(("mailto:", "tel:", "javascript:", "#")):
                    continue

                full_url = urljoin(url, href)
                full_url, _ = urldefrag(full_url)
                found_links.add(full_url)
        except Exception as e:
            print(
                f"""
                   Bir Sorun oluştu!! Bu işlem atlandı-Program çalışmaya devam ediyor. Detalar: \n Link toplama hatası: {e}
                  """
            )
            print("🔍 BS4 Tarayıcı ile tarama yapılıyor...")
            return []

        return list(found_links)
