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
            'https://wgn.pl/sprzedaz/mieszkanie/gdansk-wrzeszcz/?search%5BpriceDefTo%5D=1%2C500%2C000&search%5BsquereFrom%5D=50&search%5BsquereTo%5D=125&search%5BpriceDefm2To%5D=18%2C000&search%5BadditionalInfo%5D%5B0%5D=10'
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
                    "data_dodania": self.date_now(),
                    "fav": '0',
                    "hide": '0'
                })

                time.sleep(1)
            page += 1
        return offers
