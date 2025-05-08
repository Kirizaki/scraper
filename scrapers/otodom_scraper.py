import requests, time, re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden
from csv_writer import is_offer_saved

BASE_URL = "https://www.otodom.pl"

class OtodomScraper(RealEstateScraper):
    def scrape(self):
        offers = []
        page = 1
        while True:
            url = f"{BASE_URL}/pl/wyniki/sprzedaz/mieszkanie/pomorskie/gdansk?viewType=listing&page={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")

            offer_articles = soup.find_all("article", attrs={"data-cy": "listing-item"})
            if not offer_articles:
                break

            for offer in offer_articles:
                address = offer.find("p", class_="css-1jjm9oe e13d3jhg1") or offer.find("p", class_="css-42r2ms eejmx80")
                if not address or "wrzeszcz" not in address.text.lower():
                    continue

                link = BASE_URL + offer.find("a")['href'].split('?')[0]
                if is_offer_saved(link):
                    continue

                detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                body_text = detail_soup.get_text(separator=' ', strip=True)
                garden, snippet = has_garden(body_text)
                if not garden:
                    continue

                price = detail_soup.find("strong", {"data-testid": "ad-price"})
                area = detail_soup.find("div", string=re.compile("Powierzchnia"))
                area_val = area.find_next("div").text.strip() if area else "Brak"

                offers.append({
                    "url": link,
                    "dzielnica": address.text.strip(),
                    "cena": price.text.strip() if price else "Brak",
                    "powierzchnia": area_val,
                    "ogrod_fragment": snippet,
                    "zrodlo": "otodom",
                    "data_dodania": super().date_now()
                })

                time.sleep(0.5)
            page += 1
            time.sleep(1)
        return offers
