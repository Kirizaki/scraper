import requests, time
from bs4 import BeautifulSoup
from csv_writer import save_offer_backup
from scraper_base import RealEstateScraper
import re

class ObidoScraper(RealEstateScraper):
    BASE_URL = "https://obido.pl"

    def scrape(self):
        offers = []
        page = 1
        self.src = 'obido'
        while True:
            url = f"{self.BASE_URL}/rynek-pierwotny-trojmiasto/cena-1500000_metraz-od-50_metraz-do-120_pokoje-2i3i4i5.htm?page={page}"
            print(f"\n   [{self.src}] przeszukuje stronę (#{page}): {url}")
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")
            listings = soup.find_all("a", class_="stretched-link")
            if not listings or soup.find('div', class_="alert alert-info"):
                break

            for link in listings:
                try:
                    self.counter += 1
                    href = link["href"]
                    full_url = "https://obido.pl" + href
                    detail = requests.get(full_url, headers={"User-Agent": "Mozilla/5.0"})
                    detail_soup = BeautifulSoup(detail.text, "html.parser")
                    if not 'wrzeszcz' in detail_soup.find('ol', class_="breadcrumb").text.strip().lower():
                        continue

                    title = detail_soup.find('h1').text.strip()
                    text = detail_soup.find('section', class_="section-block investment-flat-detail").text.strip()
                    garden = self.has_garden_in_desc(text)
                    if not garden:
                        continue

                    price = self.extract_price(text)
                    area_val = self.extract_area(text)
                    floor = self.extract_floor(text)
                    if not price:
                        price = 0
                        price_per_m = 0
                    else:
                        price_per_m = int(price / area_val)

                    if area_val and (area_val < self.min_area or area_val > self.max_area):
                        continue
                    if floor > self.parter:
                        continue
                    if price_per_m > self.max_on_meter:
                        continue

                    offer = {
                        "url": full_url,
                        "tytul": title,
                        "cena": int(price),
                        "powierzchnia": int(area_val),
                        "na_metr": price_per_m,
                        "zrodlo": self.src,
                        "data_dodania": self.date_now(),
                        "fav": '0',
                        "hide": '0'
                    }
                    offers.append(offer)
                    save_offer_backup(offer, self.src+".csv")
                except Exception as e:
                    print(f"\n   [{self.src}] błąd podczas sprawdzania oferty: {full_url}:\n{e}")
                time.sleep(0.5)
            page += 1
            time.sleep(1)
        self.log()
        return offers

    def extract_floor(self, text: str) -> int:
        """
        Zwraca numer piętra jako int.
        Jeśli 'parter', zwraca 0.
        """
        text = text.lower()
        if "parter" in text:
            return 0
        match = re.search(r'(\d+)[-\s]*piętro', text)
        if match:
            return int(match.group(1))
        return 999

    def extract_price(self, text: str) -> int:
        """
        Zwraca cenę jako int. Ignoruje znaki specjalne, spacje niełamliwe itd.
        """
        match = re.search(r'cena[\s\S]{0,50}?([\d\s\xa0]+) ?zł', text.lower())
        if match:
            raw = match.group(1)
            clean = re.sub(r'[^\d]', '', raw)  # usuń wszystko co nie jest cyfrą
            return int(clean)
        return 9999999

    def extract_area(self, text: str) -> int:
        """
        Zwraca powierzchnię w metrach kwadratowych jako int.
        Zakłada, że metraż jest podany w formacie np. '61,9m2' lub '61.9 m²'.
        """
        match = re.search(r'(\d+[.,]\d+)\s?m[²2]', text.lower())
        if match:
            area = float(match.group(1).replace(",", "."))
            return round(area)
        return 999