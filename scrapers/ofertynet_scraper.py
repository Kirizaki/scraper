import requests
import time
from bs4 import BeautifulSoup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden
from urllib.parse import urljoin

BASE_URL = "https://www.oferty.net"

class OfertyNetScraper(RealEstateScraper):
    def scrape(self):
        offers = []
        page = 1
        while True:
            'https://www.oferty.net/mieszkania/szukaj?psm%5Badvanced_search%5D=1&psm%5Btype%5D=1&psm%5Bfavourites%5D=0&psm%5Blocation%5D%5Btype%5D=1&psm%5Blocation%5D%5Btext_queue%5D%5B%5D=Gda%C5%84sk+Wrzeszcz+G%C3%B3rny&psm%5Btransaction%5D=1&psm%5Bliving_area_to%5D=125&psm%5Bprice_to%5D=1500000&psm%5Bprice_m2_to%5D=18000&psm%5Bfloor_from%5D=0&psm%5Bfloor_to%5D=0&psm%5Bowner%5D%5B%5D=1&psm%5Bowner%5D%5B%5D=4&psm%5Bowner%5D%5B%5D=2&psm%5Bowner%5D%5B%5D=128&psm%5Bdate_filter%5D=0&psm%5Bsort_order%5D=added_at_desc'
            url = f"{BASE_URL}/mieszkania/sprzedaz/gdansk,wrzeszcz/?page={page}"
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
                    "zrodlo": "ofertynet",
                    "data_dodania": self.date_now(),
                    "fav": '0',
                    "hide": '0'
                })

                time.sleep(0.5)
            page += 1
            time.sleep(1)
        return offers
