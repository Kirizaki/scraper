import re
import requests
import time
from bs4 import BeautifulSoup
from csv_writer import save_offer_backup
from scraper_base import RealEstateScraper

BASE_URL = "http://nportal.pl"

class NportalScraper(RealEstateScraper):
    def scrape(self):
        self.src = 'nportal'
        offers = []
        page = 1
        while page < 999:
            url = f"{BASE_URL}/mieszkania/gdansk/?ps[sort_order]=rank&ps[price_to]=1500000&ps[living_area_to]=125&ps[floor_from]=0&ps[floor_to]=0&ps[market_type][0]=2&ps[has_balcony]=1&page={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")
            if res.status_code != 200:
                break

            if page > 1:
                real_page = self.extract_page_number(res.url)
                if not real_page or int(real_page) < page:
                    break

            soup = BeautifulSoup(res.text, "html.parser")
            offer_cards = soup.find_all("div", class_="slist")

            if not offer_cards:
                break

            for card in offer_cards:
                details = card.find("a", class_="slr_location")
                address = details.text.strip().lower()
                link = details.get('href')
                if ("wrzeszcz" in address or "oliwa" in address) and link:
                    offer = {
                        "url": link,
                        "tytul": 'title',
                        "cena": 'cena',
                        "powierzchnia": 'area',
                        "na_metr": 'per_meter',
                        "zrodlo": self.src,
                        "data_dodania": self.date_now(),
                        "fav": '0',
                        "hide": '0'
                    }
                    offers.append(offer)
                    save_offer_backup(offer, self.src + ".csv")
                continue
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
                    "zrodlo": "nportal",
                    "data_dodania": self.date_now(),
                    "fav": '0',
                    "hide": '0'
                })

                time.sleep(0.5)
            page += 1
            time.sleep(1)
        return offers

    def extract_page_number(self, path):
        match = re.search(r'page=(\d+)', path)
        return int(match.group(1)) if match else None