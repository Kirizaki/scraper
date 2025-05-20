import requests
import time
import re
from bs4 import BeautifulSoup
from csv_writer import save_offer_backup
from scraper_base import RealEstateScraper

BASE_URL = "https://adresowo.pl"

class AdresowoScraper(RealEstateScraper):
    def scrape(self):
        offers = []
        page = 1
        self.src = 'adresowo'
        while True:
            postfix = f"l{page}od"
            url = f"{BASE_URL}/f/mieszkania/gdansk/wrzeszcz/{postfix}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if page > 1:
                # strona ostatnia+1 usuwa numerek strony z URL
                current_page = self.extract_page_number(res.url)
                if current_page is None or current_page > page:
                    break
            print(f"\n   [{self.src}] przeszukuje stronę (#{page}): {url}")
            soup = BeautifulSoup(res.text, "html.parser")

            offer_articles = soup.find_all("div", class_="result-photo")
            if not offer_articles:
                break

            link = 'pierwszy_link'
            for offer in offer_articles:
                try:
                    self.counter += 1
                    link_tag = offer.parent.attrs['href']
                    if not link_tag:
                        continue
                    link = BASE_URL + link_tag

                    detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                    detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                    body_text = detail_soup.get_text(separator=' ', strip=True)
                    if not self.has_garden_in_desc(body_text):
                        continue

                    street_text = detail_soup.find('span', class_="offer-header__street").text.strip()
                    if self.has_street(street_text) and not self.proper_street(street_text):
                        continue

                    title = detail_soup.find('span', class_="offer-header__info").text.strip()
                    price = int(detail_soup.find_all("span", class_="offer-summary__value")[0].text.strip().replace(' ', ''))
                    area_val = int(detail_soup.find_all("span", class_="offer-summary__value")[1].text.strip())
                    floor = self.extract_floor(detail_soup.find_all('span', class_="offer-summary__value")[3].text.strip())
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
                except:
                    print(f"\n   [{self.src}] błąd podczas sprawdzania oferty: {link}")
                time.sleep(0.5)
            page += 1
            time.sleep(1)

        self.log()
        return offers

    def extract_page_number(self, path):
        match = re.search(r'l(\d+)od$', path)
        return int(match.group(1)) if match else None

    def extract_floor(self, text: str) -> int:
        text = text.strip().lower()

        # 'parter' -> 0
        if 'parter' in text:
            return 0

        # Poszukaj liczby na początku tekstu, np. '1', '1 / winda', ' 4/winda'
        match = re.search(r'\d+', text)
        if match:
            return int(match.group())

        # Jeśli nie znaleziono nic sensownego
        return -1  # lub None, jeśli wolisz