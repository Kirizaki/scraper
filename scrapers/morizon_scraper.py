import requests, time
from bs4 import BeautifulSoup
from csv_writer import save_offer_backup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden

BASE_URL = "https://www.morizon.pl"

class MorizonScraper(RealEstateScraper):
    def scrape(self):
        self.src = 'morizon'
        offers = []
        page = 1
        while True:
            url = f"{BASE_URL}/mieszkania/najnowsze/gdansk/wrzeszcz-gorny/?page={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            real_page = self.get_page_number(res.url)
            if not real_page or int(real_page) < page:
                break
            print(f"\n   [{self.src}] przeszukuje stronę (#{page}): {url}")
            soup = BeautifulSoup(res.text, "html.parser")

            offer_articles = soup.find_all("a", class_="RGqjO2 undefined")
            if not offer_articles:
                break
            for offer in offer_articles:
                self.counter += 1
                link = BASE_URL + offer.get("href")

                detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                body_text = detail_soup.get_text(separator=' ', strip=True)
                garden, snippet = has_garden(body_text)
                if not garden:
                    continue

                title = detail_soup.find("h1").contents[0]
                price = detail_soup.find("div", class_="Fzi-XT").text.strip()
                area_val = detail_soup.find("div", class_="property-info").contents[0].text.strip()

                offer = {
                    "url": link,
                    "tytul": title,
                    "dzielnica": "Wrzeszcz",
                    "cena": price,
                    "powierzchnia": area_val,
                    "ogrod_fragment": snippet,
                    "zrodlo": "adresowo",
                    "data_dodania": super().date_now()
                }
                offers.append(offer)
                save_offer_backup(offer, self.src+".csv")     
                time.sleep(0.5)
            page += 1
            time.sleep(1)

        self.log()
        return offers
