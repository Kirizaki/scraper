import requests, time
from bs4 import BeautifulSoup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden

class TrovitScraper(RealEstateScraper):
    BASE_URL = "https://dom.trovit.pl/index.php/cod.search_homes"

    def scrape(self):
        offers = []
        page = 1
        while True:
            params = {
                'what_d': 'mieszkania',
                'where': 'Gda%C5%84sk%2C+Pomorskie',
                'tp': '1',  # sprzedaż
                'page': page
            }
            res = requests.get(self.BASE_URL, params=params, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")
            listings = soup.select(".item-info-container")
            if not listings:
                break

            for item in listings:
                title_el = item.find("a", class_="item-title")
                if not title_el:
                    continue
                url = title_el["href"]
                if "wrzeszcz" not in title_el.text.lower():
                    continue

                detail = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                detail_soup = BeautifulSoup(detail.text, "html.parser")
                text = detail_soup.get_text(" ", strip=True)
                garden, snippet = has_garden(text)
                if not garden:
                    continue

                price = item.select_one(".price")
                offers.append({
                    "url": url,
                    "tytul": title_el.text.strip(),
                    "dzielnica": "Wrzeszcz",
                    "cena": price.text.strip() if price else "",
                    "powierzchnia": "",
                    "ogrod_fragment": snippet,
                    "zrodlo": "trovit",
                    "data_dodania": self.date_now()
                })

                time.sleep(0.5)
            page += 1
            time.sleep(1)
        return offers