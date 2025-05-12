import requests
import time
from bs4 import BeautifulSoup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden
from urllib.parse import urljoin

BASE_URL = "https://www.nokaut.pl"

class NokautScraper(RealEstateScraper):
    def scrape(self):
        offers = []
        page = 1
        while True:
            url = f"{BASE_URL}/nieruchomosci/mieszkania/sprzedaz/gdansk-wrzeszcz/?p={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code != 200 or "brak wyników" in res.text.lower():
                break

            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.find_all("div", class_="product-box")
            if not items:
                break

            for item in items:
                title_tag = item.find("a", class_="product-link")
                if not title_tag:
                    continue

                link = urljoin(BASE_URL, title_tag['href'])

                detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                body_text = detail_soup.get_text(separator=' ', strip=True)
                garden, snippet = has_garden(body_text)
                if not garden:
                    continue

                title = title_tag.text.strip()
                address = "Wrzeszcz, Gdańsk"
                price_tag = item.find("span", class_="price")
                price = price_tag.text.strip() if price_tag else "Brak ceny"
                area = "Brak danych"

                offers.append({
                    "url": link,
                    "tytul": title,
                    "dzielnica": address,
                    "cena": price,
                    "powierzchnia": area,
                    "ogrod_fragment": snippet,
                    "zrodlo": "nokaut",
                    "data_dodania": self.date_now(),
                    "fav": '0',
                    "hide": '0'
                })

                time.sleep(0.5)

            page += 1
            time.sleep(1)

        return offers
