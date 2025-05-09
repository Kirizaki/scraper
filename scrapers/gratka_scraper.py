import requests, time
from bs4 import BeautifulSoup
from csv_writer import save_offer_backup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden

BASE_URL = "https://gratka.pl"

class GratkaScraper(RealEstateScraper):
    def scrape(self):
        offers = []
        page = 1
        self.src = 'gratka'
        while True:
            url = f"{BASE_URL}/nieruchomosci/mieszkania/gdansk/wrzeszcz?cena-calkowita:min=300000&cena-calkowita:max=10000000&sort=newest&page={page}"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")
            current_page = self.extract_page_number(soup)

            if current_page is None or current_page < page:
                break
            print(f"\n   [{self.src}] przeszukuje stronę (#{page}): {url}")

            offer_articles = soup.find_all("a", class_="RGqjO2 undefined")
            if not offer_articles:
                break

            for offer in offer_articles:
                self.counter += 1
                link = f'{BASE_URL}{offer.get("href")}'
                detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                body_text = detail_soup.get_text(separator=' ', strip=True)
                garden, snippet = has_garden(body_text)
                if not garden:
                    continue

                title = detail_soup.find("h1").text.strip()
                price = detail_soup.find("div", class_="Fzi-XT").string
                area_val = detail_soup.find("div", class_="property-info").contents[0].contents[0]

                offer = {
                   "url": link,
                    "tytul": title,
                    "dzielnica": "Wrzeszcz",  # Gratka ma gorsze dzielenie na dzielnice
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

    def extract_page_number(self, soup):
        try:
            return int(soup.find("div", class_="ACyYX6 GWviLn J-2bfe KBA9kE YTX4Au").text.strip())
        except:
            pass
        return None
    