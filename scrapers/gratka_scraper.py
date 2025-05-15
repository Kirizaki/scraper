import requests
import time
import re
from bs4 import BeautifulSoup
from bs4 import Tag
from typing import List, Optional
from csv_writer import save_offer_backup
from scraper_base import RealEstateScraper

BASE_URL = "https://gratka.pl"

class GratkaScraper(RealEstateScraper):
    def scrape(self):
        offers = []
        page = 1
        self.src = 'gratka'
        while True:
            url = f"{BASE_URL}/nieruchomosci/mieszkania/gdansk/wrzeszcz?cena-calkowita:min=300000&cena-calkowita:max=10000000&sort=newest&page={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")

            current_page = self.extract_page_number(soup)
            if current_page is None or current_page < page:
                break

            print(f"\n   [{self.src}] przeszukuje stronę (#{page}): {url}")

            offer_articles = soup.find_all("a", class_="RGqjO2 undefined")
            if not offer_articles:
                break

            link = 'pierwszy_link'
            for offer in offer_articles:
                try:
                    self.counter += 1
                    link_tag = offer.get("href")
                    if not link_tag:
                        continue
                    link = f"{BASE_URL}{link_tag}"

                    detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                    detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                    body_text = detail_soup.find('div', class_="Dx7LS- OUtXFF ofQE0x").text.strip()
                    details = detail_soup.find('div', class_="XMKqaz").text.strip()
                    if not self.has_garden_in_desc(body_text) and not self.has_garden_in_desc(details):
                        continue

                    # Nazwa ulicy — do ew. walidacji
                    street_text = detail_soup.find("span", class_="_4peQ6d yxGIU-").text.strip()
                    if self.has_street(street_text) and not self.proper_street(street_text):
                        continue

                    # Tytuł
                    title = detail_soup.find("h1").text.strip()

                    # Cena
                    try:
                        price = detail_soup.find("span", class_="maMBkV").text.strip().replace(' ', '').replace('zł', '').replace('zl', '')
                    except:
                        continue

                    additional_details = detail_soup.find('div', class_="TocF4V").find_all('span')
                    # Powierzchnia
                    try:
                        area_val = self.extract_area_from_spans(additional_details)
                    except:
                        continue

                    # Piętro
                    try:
                        floor = self.extract_floor_from_spans(additional_details)
                    except:
                        floor = 999

                    price_per_m = price / area_val if area_val else 0

                    if area_val and (area_val < self.min_area or area_val > self.max_area):
                        continue
                    if floor > self.parter:
                        continue
                    if price_per_m > self.max_on_meter:
                        continue

                    offer = {
                        "url": link,
                        "tytul": title,
                        "cena": price,
                        "powierzchnia": area_val,
                        "na_metr": price_per_m,
                        "zrodlo": self.src,
                        "data_dodania": self.date_now(),
                        "fav": '0',
                        "hide": '0'
                    }
                    offers.append(offer)
                    save_offer_backup(offer, self.src + ".csv")
                except:
                    print(f'[{self.src}] błąd podczas sprawdzania oferty: {link}')
                time.sleep(0.5)

            page += 1
            time.sleep(1)

        self.log()
        return offers

    def extract_page_number(self, soup):
        try:
            return int(soup.find('a', class_="router-link-active router-link-exact-active").text.strip())
        except:
            return None

    def extract_floor_from_spans(self, spans: List[Tag]) -> Optional[int]:
        for span in spans:
            text = span.get_text(strip=True).lower()
            if 'piętro' in text:
                match = re.search(r'piętro\s*(\d+)', text)
                if match:
                    return int(match.group(1))
                elif 'parter' in text:
                    return 0
        return 999


    def extract_area_from_spans(self, spans: List[Tag]) -> Optional[int]:
        for span in spans:
            text = span.get_text(strip=True).lower()
            match = re.search(r'(\d+[.,]?\d*)\s*m²', text)
            if match:
                area = float(match.group(1).replace(',', '.'))
                return int(area)  # zwracamy jako int (np. 48.66 → 48)
        return 99999

    def extract_floor(self, text: str) -> int:
        text = text.strip().lower()
        if 'parter' in text:
            return 0
        match = re.search(r'\d+', text)
        return int(match.group()) if match else -1
