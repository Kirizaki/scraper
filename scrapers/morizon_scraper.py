import requests
import time
import re
from bs4 import BeautifulSoup
from csv_writer import save_offer_backup
from scraper_base import RealEstateScraper

BASE_URL = "https://www.morizon.pl"

class MorizonScraper(RealEstateScraper):
    def scrape(self):
        self.src = 'morizon'
        offers = []
        page = 1

        while True:
            url = f"{BASE_URL}/mieszkania/najnowsze/gdansk/wrzeszcz-gorny/?page={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if page > 1:
                real_page = self.extract_page_number(res.url)
                if not real_page or int(real_page) < page:
                    break

            print(f"\n   [{self.src}] przeszukuje stronę (#{page}): {url}")
            soup = BeautifulSoup(res.text, "html.parser")
            offer_articles = soup.find_all("a", class_="RGqjO2")
            if not offer_articles:
                break

            link = 'pierwszy_link'
            for offer in offer_articles:
                try:
                    self.counter += 1
                    link = BASE_URL + offer.get("href")
                    detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                    detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                    body_text = detail_soup.find('div', class_="jda-sU OUtXFF ofQE0x").text.strip()

                    if not self.has_garden_in_desc(body_text):
                        continue

                    spans = detail_soup.find_all("span")
                    area_val = self.extract_area_from_spans(spans)
                    floor = self.extract_floor_from_spans(spans)
                    if area_val is None or floor is None:
                        continue

                    if area_val < self.min_area or area_val > self.max_area:
                        continue
                    if floor > self.parter:
                        continue

                    price_text = detail_soup.find("div", class_="Fzi-XT").text.strip().replace(' ', '').replace('zł', '')
                    price = int(price_text) if price_text.isdigit() else 0
                    if price == 0:
                        continue

                    price_per_m = price / area_val if area_val else 0
                    if price_per_m > self.max_on_meter:
                        continue

                    title = detail_soup.find("h1").text.strip()

                    offer = {
                        "url": link,
                        "tytul": title,
                        "cena": int(price),
                        "powierzchnia": int(area_val),
                        "na_metr": int(price_per_m),
                        "zrodlo": self.src,
                        "data_dodania": self.date_now(),
                        "fav": '0',
                        "hide": '0'
                    }
                    offers.append(offer)
                    save_offer_backup(offer, self.src+".csv")

                except Exception as e:
                    print(f"[{self.src}] błąd podczas sprawdzania oferty: {link} ({e})")
                time.sleep(0.5)

            page += 1
            time.sleep(1)

        self.log()
        return offers

    def extract_page_number(self, path):
        match = re.search(r'page=(\d+)', path)
        return int(match.group(1)) if match else None

    def extract_area_from_spans(self, spans):
        for span in spans:
            text = span.get_text(strip=True).lower()
            match = re.search(r'(\d+[.,]?\d*)\s*m²', text)
            if match:
                return int(float(match.group(1).replace(',', '.')))
        return None

    def extract_floor_from_spans(self, spans):
        for span in spans:
            text = span.get_text(strip=True).lower()
            if 'piętro' in text:
                if 'parter' in text:
                    return 0
                match = re.search(r'piętro\s*(\d+)', text)
                if match:
                    return int(match.group(1))
        return None
