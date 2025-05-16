import requests
import time
from bs4 import BeautifulSoup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden
from urllib.parse import urljoin

BASE_URL = "https://sprzedajemy.pl"

class SprzedajemyScraper(RealEstateScraper):
    def scrape(self):
        offers = []
        page = 1
        while True:
            'https://sprzedajemy.pl/nieruchomosci/mieszkania/sprzedaz?inp_price%5Bto%5D=1500000&amp;inp_attribute_143%5Bto%5D=125&amp;inp_attribute_149%5B0%5D=618&amp;inp_attribute_150%5Bfrom%5D=0&amp;inp_attribute_150%5Bto%5D=0&amp;inp_attribute_252%5Bto%5D=18000'
            url = f"{BASE_URL}/nieruchomosci/mieszkania/gdansk/wrzeszcz?page={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code != 200:
                break

            soup = BeautifulSoup(res.text, "html.parser")
            offer_cards = soup.find_all("div", class_="listing__item")

            if not offer_cards:
                break

            for card in offer_cards:
                link_tag = card.find("a", class_="listing__link")
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

                title = detail_soup.find("h1").text.strip() if detail_soup.find("h1") else "Brak tytułu"
                price_tag = detail_soup.find("strong", class_="price__value")
                price = price_tag.text.strip() if price_tag else "Brak ceny"

                # Powierzchnię próbujemy wyciągnąć z opisu (jeśli nie ma osobnego pola)
                area = "Nieznana"
                desc = detail_soup.find("div", class_="description__text")
                if desc:
                    area_match = self.extract_area(desc.text)
                    if area_match:
                        area = area_match

                offers.append({
                    "url": link,
                    "tytul": title,
                    "dzielnica": "Wrzeszcz",
                    "cena": price,
                    "powierzchnia": area,
                    "ogrod_fragment": snippet,
                    "zrodlo": "sprzedajemy",
                    "data_dodania": self.date_now(),
                    "fav": '0',
                    "hide": '0'
                })

                time.sleep(0.5)
            page += 1
            time.sleep(1)
        return offers

    def extract_area(self, text):
        import re
        match = re.search(r"(\d{2,3})\s?m", text.lower())
        return f"{match.group(1)} m²" if match else None
