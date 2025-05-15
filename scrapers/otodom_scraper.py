import requests, time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from csv_writer import save_offer_backup
from scraper_base import RealEstateScraper

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

            link = 'pierwszy_link'
            for offer in offer_articles:
                try:
                    address = offer.find("p", class_="css-1jjm9oe e13d3jhg1") or offer.find("p", class_="css-42r2ms eejmx80")
                    if not address or "wrzeszcz" not in address.text.lower():
                        continue

                    street_text = offer.find('p', class_="css-42r2ms eejmx80").text
                    if self.has_street(street_text) and not self.proper_street(street_text):
                        continue

                    self.counter += 1
                    link = BASE_URL + offer.find("a")['href'].split('?')[0]

                    detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                    detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                    details = detail_soup.find_all("span", class_="css-axw7ok esen0m94")
                    if not self.has_garden_in_additional_info(details):
                        continue

                    title = detail_soup.find("h1").text.strip()
                    price = detail_soup.find("strong", class_="css-1o51x5a e1k1vyr21").contents[0].text.strip()

                    area_val = self.extract_surface(offer.find('dl', class_="css-9q2yy4 eyjpr0t1").text)
                    if area_val and (area_val < self.min_area or area_val > self.max_area):
                        continue

                    floor = self.extract_floor(offer.find('dl', class_="css-9q2yy4 eyjpr0t1").text)
                    if floor > self.parter:
                        continue

                    price = self.extract_price(detail_soup.find('strong', class_="css-1o51x5a e1k1vyr21").text)
                    price_on_meter = self.extract_price(detail_soup.find('div', class_="css-z3xj2a e1k1vyr25").text)
                    if price_on_meter and price_on_meter > self.max_on_meter:
                        continue

                    offer = {
                        "url": link,
                        "tytul": title,
                        "cena": int(price),
                        "powierzchnia": int(area_val),
                        "na_metr": int(price_on_meter),
                        "zrodlo": self.src,
                        "data_dodania": self.date_now(),
                        "fav": '0',
                        "hide": '0'
                    }
                    offers.append(offer)
                    save_offer_backup(offer, self.src+".csv")
                except:
                    print(f'[{self.src}] błąd podczas sprawdzania oferty: {link}')
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
