import requests, time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from csv_writer import save_offer_backup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden

BASE_URL = "https://www.otodom.pl"

class OtodomScraper(RealEstateScraper):
    def scrape(self):
        offers = []
        page = 1
        last_real_page = None
        self.src = 'otodom'
        while True:
            url = f"{BASE_URL}/pl/wyniki/sprzedaz/mieszkanie/pomorskie/gdansk?viewType=listing&page={page}&by=LATEST&direction=DESC"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, "html.parser")

            # Wyciągamy numer strony z URL
            current_page = self.get_page_number_from_url(res.url)
            if current_page is None or current_page < page:
                print("Błąd podczas wyciągania numeru strony!")
                break

            # Jeśli numer strony się nie zmienia, oznacza to, że osiągnęliśmy ostatnią stronę
            if current_page == last_real_page:
                print("Osiągnięto koniec listy ofert.")
                break

            print(f"\n   [{self.src}] przeszukuje stronę (#{page}): {url}")
            offer_articles = soup.find_all("article", attrs={"data-cy": "listing-item"})
            if not offer_articles:
                break

            for offer in offer_articles:
                address = offer.find("p", class_="css-1jjm9oe e13d3jhg1") or offer.find("p", class_="css-42r2ms eejmx80")
                if not address or "wrzeszcz" not in address.text.lower():
                    continue
                self.counter += 1
                link = BASE_URL + offer.find("a")['href'].split('?')[0]

                detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                body_text = detail_soup.get_text(separator=' ', strip=True)
                garden, snippet = has_garden(body_text)
                if not garden:
                    continue

                title = detail_soup.find("h1").text.strip()
                price = detail_soup.find("strong", class_="css-1o51x5a e1k1vyr21").contents[0].text.strip()
                area_val = detail_soup.find_all("p", class_="esen0m92 css-1airkmu")[1].text.strip

                offer = {
                    "url": link,
                    "tytul": title,
                    "dzielnica": address.text.strip(),
                    "cena": price,
                    "powierzchnia": area_val,
                    "ogrod_fragment": snippet,
                    "zrodlo": self.src,
                    "data_dodania": self.date_now()
                }
                offers.append(offer)
                save_offer_backup(offer, self.src+".csv")

                time.sleep(0.5)
            page += 1
            time.sleep(1)
        self.log()
        return offers

    def get_page_number_from_url(self, url):
        """Zwraca numer strony wyciągnięty z URL"""
        parsed_url = urlparse(url)
        page_number = parse_qs(parsed_url.query).get('page', [None])[0]
        if page_number:
            return int(page_number)
        return None
