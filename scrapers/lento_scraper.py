import requests, time
from bs4 import BeautifulSoup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden

class LentoScraper(RealEstateScraper):
    BASE_URL = "https://gdansk.lento.pl/nieruchomosci/mieszkania-sprzedaz.html"

    def scrape(self):
        offers = []
        page = 1
        while True:
            url = f"{self.BASE_URL}?page={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")
            listings = soup.select(".ad-box")
            if not listings:
                break

            for box in listings:
                title_el = box.select_one("h2 a")
                if not title_el or "wrzeszcz" not in title_el.text.lower():
                    continue

                link = title_el["href"]
                full_url = link if link.startswith("http") else f"https:{link}"
                detail = requests.get(full_url, headers={"User-Agent": "Mozilla/5.0"})
                detail_soup = BeautifulSoup(detail.text, "html.parser")
                text = detail_soup.get_text(" ", strip=True)
                garden, snippet = has_garden(text)
                if not garden:
                    continue

                offers.append({
                    "url": full_url,
                    "tytul": title_el.text.strip(),
                    "dzielnica": "Wrzeszcz",
                    "cena": "",  # Lento rzadko podaje bez logowania
                    "powierzchnia": "",
                    "ogrod_fragment": snippet,
                    "zrodlo": "lento",
                    "data_dodania": self.date_now()
                })
                time.sleep(0.5)
            page += 1
            time.sleep(1)
        return offers