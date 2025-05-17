import requests
import time
import re
from bs4 import BeautifulSoup
from scraper_base import RealEstateScraper
from csv_writer import is_offer_saved, save_offer_backup

BASE_URL = "https://www.nieruchomosci-online.pl"

class NieruchomosciOnlineScraper(RealEstateScraper):
    def scrape(self):
        offers = []
        page = 1
        self.src = 'nieruchomosci'
        current_page_number = page
        while True:
            url = f"{BASE_URL}/szukaj.html?3,mieszkanie,sprzedaz,,Gda%C5%84sk:7183,Wrzeszcz%20G%C3%B3rny:23156,,,-1500000,50-120&p={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")
            try:
                current_page_number = soup.find('ul', class_="pagination-mob-sub").find('span', class_='active').text.strip()
            except:
                print(f'[{self.src}] problem z wyciaganiem numeru strony dla: {url}')

            if current_page_number and int(current_page_number) != page:
                break

            print(f"\n   [{self.src}] przeszukuje stronę (#{page}): {url}")
            offer_articles = soup.find_all('a', class_="tabCtrl")
            if not offer_articles:
                offer_articles = soup.find_all('span', class_="alike")
                if not offer_articles:
                    break

            link = "pierwszy_link"
            for offer in offer_articles:
                try:
                    link = offer.get('href')
                    if not link:
                        continue

                    self.counter += 1
                    detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                    detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                    body_text = detail_soup.find('div', class_="box-offer-inside box-offer-inside__as").text.strip()
                    garden = self.has_garden_in_desc(body_text)
                    if not garden:
                        continue

                    title = detail_soup.find("h1").text.strip()
                    price = self.extract_price(body_text)
                    area_val = self.extract_area(body_text)
                    floor = self.extract_floor(body_text)
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
                    print(f"[{self.src}] błąd podczas sprawdzania oferty: {link}\n{e}")
                time.sleep(0.5)
            
            page += 1
            time.sleep(1)
        self.log()
        return offers

    def extract_price(self, text: str) -> int:
        """
        Wyciąga cenę mieszkania jako liczbę całkowitą w złotówkach.
        """
        match = re.search(r'Cena:\s*([\d\s]+)\s*zł', text)
        if match:
            return int(match.group(1).replace('\xa0', '').replace(' ', ''))
        return 0

    def extract_area(self, text: str) -> float:
        """
        Wyciąga powierzchnię mieszkania w metrach kwadratowych.
        """
        match = re.search(r'Charakterystyka mieszkania:\s*([\d,]+)\s*m²', text)
        if match:
            return float(match.group(1).replace(',', '.').replace('\xa0', ''))
        return 999

    def extract_floor(self, text: str) -> int:
        """
        Wyciąga piętro mieszkania jako liczbę całkowitą.
        Jeśli znajdzie 'parter', zwróci 0.
        """
        # najpierw sprawdzamy, czy jest słowo "parter"
        if 'parter' in text.lower():
            return 0

        # potem próbujemy wyciągnąć liczbę po słowie 'piętro'
        match = re.search(r'piętro\s*(\d+)', text.lower())
        if match:
            return int(match.group(1))

        return 999
