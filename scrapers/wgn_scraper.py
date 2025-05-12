import requests
import time
from bs4 import BeautifulSoup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden

BASE_URL = "https://www.wgn.pl"

class WGNScraper(RealEstateScraper):
    def scrape(self):
        offers = []
        page = 1
        while True:
            url = f"{BASE_URL}/mieszkania/sprzedaz/gdansk?strona={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")

            offer_articles = soup.find_all("div", class_="offer-item")
            if not offer_articles:
                break

            for offer in offer_articles:
                link_tag = offer.find("a", href=True)
                if not link_tag:
                    continue
                link = BASE_URL + link_tag['href']

                detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                body_text = detail_soup.get_text(separator=' ', strip=True)
                garden, snippet = has_garden(body_text)
                if not garden:
                    continue

                title = detail_soup.find("h1", class_="offer-title").text.strip()
                price = detail_soup.find("span", class_="price").text.strip()
                area_val = detail_soup.find("span", class_="area").text.strip()

                offers.append({
                    "url": link,
                    "tytul": title,
                    "dzielnica": "wrzeszcz",
                    "cena": price,
                    "powierzchnia": area_val,
                    "ogrod_fragment": snippet,
                    "zrodlo": "wgn",
                    "data_dodania": self.date_now()
                })

                time.sleep(1)
            page += 1
        return offers
