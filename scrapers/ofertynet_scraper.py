import re
import requests
import time
from bs4 import BeautifulSoup
from csv_writer import save_offer_backup
from scraper_base import RealEstateScraper

BASE_URL = "https://www.oferty.net"

class OfertyNetScraper(RealEstateScraper):
    def scrape(self):
        self.src = 'oferty_net'
        offers = []
        page = 1
        while page < 999:
            url = f"{BASE_URL}/mieszkania/szukaj?psm%5Badvanced_search%5D=1&psm%5Btype%5D=1&psm%5Bfavourites%5D=0&psm%5Blocation%5D%5Btype%5D=1&psm%5Blocation%5D%5Btext_queue%5D%5B%5D=Gda%C5%84sk+Wrzeszcz+G%C3%B3rny&psm%5Blocation%5D%5Btext_queue%5D%5B%5D=Gda%C5%84sk+Oliwa&psm%5Btransaction%5D=1&psm%5Bliving_area_to%5D=125&psm%5Bprice_to%5D=1500000&psm%5Bprice_m2_to%5D=18000&psm%5Bfloor_from%5D=0&psm%5Bfloor_to%5D=0&psm%5Bowner%5D%5B%5D=1&psm%5Bowner%5D%5B%5D=4&psm%5Bowner%5D%5B%5D=2&psm%5Bowner%5D%5B%5D=128&psm%5Bdate_filter%5D=0&psm%5Bsort_order%5D=added_at_desc&page={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code != 200:
                break

            soup = BeautifulSoup(res.text, "html.parser")
            offer_cards = soup.find_all("tr", class_="property oddRow")

            if not offer_cards:
                break

            print(f"\n   [{self.src}] przeszukuje stronę (#{page}): {url}")
            for card in offer_cards:
                match = re.search(r"openOffer\(event,'(https://[^']+)'", card.get('onclick'))
                if match:
                    link = match.group(1)
                    self.counter += 1
                    offer = {
                        "url": link,
                        "tytul": 'title',
                        "cena": 'cena',
                        "powierzchnia": 'powierzchnia',
                        "na_metr": 'per_meter',
                        "zrodlo": self.src,
                        "data_dodania": self.date_now(),
                        "fav": '0',
                        "hide": '0'
                    }
                    offers.append(offer)
                    save_offer_backup(offer, self.src+".csv")
                continue

                time.sleep(0.5)
            page += 1
            time.sleep(1)
        return offers
