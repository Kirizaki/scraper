import requests
import time
import re
from bs4 import BeautifulSoup
from csv_writer import save_offer_backup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden

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

            for offer in offer_articles:
                self.counter += 1
                link_tag = offer.parent.attrs['href']
                if not link_tag:
                    continue
                link = BASE_URL + link_tag

                detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                body_text = detail_soup.get_text(separator=' ', strip=True)
                garden, snippet = has_garden(body_text)
                if not garden:
                    continue

                title_parts = detail_soup.find("h1").text.split('\n')
                title = title_parts[1] + ", " + title_parts[2]
                price = detail_soup.find_all("span", class_="offer-summary__value")[0].text.strip()
                area_val = detail_soup.find_all("span", class_="offer-summary__value")[1].text.strip()

                offer = {
                    "url": link,
                    "tytul": title,
                    "dzielnica": "Wrzeszcz",
                    "cena": price,
                    "powierzchnia": area_val,
                    "ogrod_fragment": snippet,
                    "zrodlo": self.src,
                    "data_dodania": super().date_now()
                }
                offers.append(offer)
                save_offer_backup(offer, self.src+".csv")
                time.sleep(0.5)
            page += 1
            time.sleep(1)

        self.log()
        return offers

    def extract_page_number(self, path):
        match = re.search(r'l(\d+)od$', path)
        return int(match.group(1)) if match else None
