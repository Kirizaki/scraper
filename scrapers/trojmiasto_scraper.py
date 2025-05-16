import requests
import time
from bs4 import BeautifulSoup
from csv_writer import save_offer_backup
from scraper_base import RealEstateScraper
from urllib.parse import urljoin

BASE_URL = "https://ogloszenia.trojmiasto.pl"

class TrojmiastoScraper(RealEstateScraper):
    def scrape(self):
        offers = []
        page = 0
        self.src = 'trojmiasto'
        self.counter = 0
        while True:
            url = f"{BASE_URL}/nieruchomosci/mieszkanie/gdansk/wrzeszcz/ai,_1500000,ikl,101_106,qi,_120,si,-1_-1,o1,1.html?strona={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code != 200:
                break

            print(f"\n   [{self.src}] przeszukuje stronę (#{page}): {url}")
            soup = BeautifulSoup(res.text, "html.parser")
            offer_cards = soup.find_all("a", class_="listItemFirstPhoto")

            if not offer_cards:
                break

            for card in offer_cards:
                try:
                    link = card.get('href')
                    if not link:
                        continue

                    self.counter += 1
                    detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                    if detail_res.status_code != 200:
                        continue

                    detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                    details = detail_soup.find('ul', class_="oglFieldList").text.strip()
                    garden = self.has_garden_in_desc(details)
                    if not garden:
                        continue

                    title = detail_soup.find("h1", class_="xogIndex__title").text.strip()
                    price = int(float(detail_soup.find('p', class_="xogField__value xogField__value--bigPrice autolinkSafariFix").text.strip().replace('zl', '').replace('zł', '').replace(' ', '').replace(',', '.')))
                    area_val = int(float(detail_soup.find('span', class_="xogField__value xogField__value--big").text.strip().replace('\n', '')[0:5].strip().replace(',', '.')))
                    floor = self.extract_floor(detail_soup)
                    price_per_m = int(price / area_val)

                    if area_val and (area_val < self.min_area or area_val > self.max_area):
                        continue
                    if floor > self.parter:
                        continue
                    if price_per_m > self.max_on_meter:
                        continue

                    offer = {
                        "url": link,
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
                    print(f"[{self.src}] błąd podczas sprawdzania oferty: {link}:\n{e}")
                time.sleep(0.5)
            page += 1
            time.sleep(1)
        self.log()
        return offers

    def extract_floor(self, soup):
        pietro_elem = soup.find("a", class_="xogField--pietro")
        if not pietro_elem:
            return None
        text = pietro_elem.get_text(strip=True).lower()
        if "parter" in text:
            return 0
        for s in text.split():
            if s.isdigit():
                return int(s)
        return None