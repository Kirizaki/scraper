import requests
import time
from bs4 import BeautifulSoup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden

BASE_URL = "https://www.domiporta.pl"

class DomiportaScraper(RealEstateScraper):
    def scrape(self):
        offers = []
        page = 1
        while True:
            'https://www.domiporta.pl/mieszkanie/sprzedam/pomorskie/gdansk/wrzeszcz?Surface.To=125&PricePerMeter.To=1500000&Pietro.From=0&Pietro.To=0&EstateFacilities=ogr%C3%B3dek.10571'
            url = f"{BASE_URL}/mieszkanie/sprzedam/pomorskie/gdansk/wrzeszcz?page={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")

            offer_articles = soup.find_all("article", class_="listing__item")
            if not offer_articles:
                break

            for offer in offer_articles:
                link_tag = offer.find("a", href=True)
                if not link_tag:
                    continue
                link = BASE_URL + link_tag['href'].split('?')[0]

                detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                body_text = detail_soup.get_text(separator=' ', strip=True)
                garden, snippet = has_garden(body_text)
                if not garden:
                    continue

                title = detail_soup.find("h1").text.strip()
                price = detail_soup.find("span", class_="price").text.strip()
                area_el = detail_soup.find("li", class_="area")
                area_val = area_el.text.strip() if area_el else "?"

                offers.append({
                    "url": link,
                    "tytul": title,
                    "dzielnica": "Wrzeszcz",
                    "cena": price,
                    "powierzchnia": area_val,
                    "ogrod_fragment": snippet,
                    "zrodlo": "domiporta",
                    "data_dodania": self.date_now(),
                    "fav": '0',
                    "hide": '0'
                })
                time.sleep(0.5)
            page += 1
            time.sleep(1)
        return offers
