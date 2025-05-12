import requests, time
from bs4 import BeautifulSoup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden

class ObidoScraper(RealEstateScraper):
    BASE_URL = "https://obido.pl/szukaj/mieszkania/gdansk-wrzeszcz/"

    def scrape(self):
        offers = []
        page = 1
        while True:
            url = f"{self.BASE_URL}?page={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")
            listings = soup.find_all("a", class_="listing-tile")
            if not listings:
                break

            for link in listings:
                href = link["href"]
                full_url = "https://obido.pl" + href
                detail = requests.get(full_url, headers={"User-Agent": "Mozilla/5.0"})
                detail_soup = BeautifulSoup(detail.text, "html.parser")
                text = detail_soup.get_text(" ", strip=True)
                garden, snippet = has_garden(text)
                if not garden:
                    continue

                title = detail_soup.find("h1")
                price = detail_soup.select_one(".price")
                offers.append({
                    "url": full_url,
                    "tytul": title.text.strip() if title else "",
                    "dzielnica": "Wrzeszcz",
                    "cena": price.text.strip() if price else "",
                    "powierzchnia": "",
                    "ogrod_fragment": snippet,
                    "zrodlo": "obido",
                    "data_dodania": self.date_now()
                })
                time.sleep(0.5)
            page += 1
            time.sleep(1)
        return offers