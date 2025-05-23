import requests
import time
from bs4 import BeautifulSoup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden
from urllib.parse import urljoin

BASE_URL = "https://www.housemarket.pl"

class HouseMarketScraper(RealEstateScraper):
    def scrape(self):
        offers = []
        page = 1
        while True:
            'https://www.housemarket.pl/oferty/nieruchomosci/?nieruchomosci_miejscowosc=Gda%C5%84sk&nieruchomosci_miejscowosc_id=97&cenaOd=-1&cenaDo=1500000&metrazOd=-1&metrazDo=125&pietroOd=0&pietroDo=0'
            url = f"{BASE_URL}/oferty/nieruchomosci/gdansk/wrzeszcz/?page={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code != 200:
                break

            soup = BeautifulSoup(res.text, "html.parser")
            offer_cards = soup.find_all("div", class_="offer-card")

            if not offer_cards:
                break

            for card in offer_cards:
                link_tag = card.find("a", class_="offer-link")
                if not link_tag:
                    continue

                link = urljoin(BASE_URL, link_tag['href'])

                detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                if detail_res.status_code != 200:
                    continue

                detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                body_text = detail_soup.get_text(separator=' ', strip=True)
                garden, snippet = has_garden(body_text)
                if not garden:
                    continue

                title_tag = detail_soup.find("h1")
                title = title_tag.text.strip() if title_tag else "Brak tytułu"

                price_tag = detail_soup.find("span", class_="price")
                price = price_tag.text.strip() if price_tag else "Brak ceny"

                area_tag = detail_soup.find("span", class_="area")
                area = area_tag.text.strip() if area_tag else "Nieznana"

                offers.append({
                    "url": link,
                    "tytul": title,
                    "dzielnica": "Wrzeszcz",
                    "cena": price,
                    "powierzchnia": area,
                    "ogrod_fragment": snippet,
                    "zrodlo": "housemarket",
                    "data_dodania": self.date_now(),
                    "fav": '0',
                    "hide": '0'
                })

                time.sleep(0.5)
            page += 1
            time.sleep(1)
        return offers
