import shutil
import requests, re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tempfile
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from scraper_base import RealEstateScraper
from csv_writer import save_offer_backup

BASE_URL = "https://www.olx.pl"

class OlxScraper(RealEstateScraper):
    def scrape(self):
        # Unikalny katalog dla profilu
        user_data_dir = tempfile.mkdtemp(prefix="selenium_profile_")
        self.driver = self.init_driver(user_data_dir)
        try:
            self.src = 'olx'
            offers = []
            page = 1
            last_real_page = None
            while True:
                url = f"https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/gdansk/?page={page}&search%5Bdistrict_id%5D=99&search%5Border%5D=created_at%3Adesc"
                self.driver.get(url)
                self.scroll_to_load_all()
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')

                # Wyciągamy numer strony z URL
                current_page = int(soup.find("li", class_="pagination-item__active").text.strip())
                if current_page is None or current_page < page or current_page == last_real_page:
                    print(f"[{self.src}]Osiągnięto koniec listy ofert.")
                    break

                print(f"\n   [{self.src}] przeszukuje stronę (#{page}): {self.driver.current_url}")

                link_elements = soup.find_all("a", class_="css-1tqlkj0")
                print(f"[{self.src}]🔗 Znaleziono {len(link_elements)} ofert po pełnym scrollu.")
                link = 'pierwszy_link'
                for link_element in link_elements:
                    if 'otodom.pl' in link_element.get("href"):
                        continue

                    link = f'{BASE_URL}{link_element.get("href")}'
                    try:
                        self.counter += 1
                        detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
                        detail_soup = BeautifulSoup(detail_res.text, "html.parser")

                        body_text = detail_soup.get_text(separator=' ', strip=True)
                        if "wrzeszcz" not in body_text.lower():
                            continue

                        street_text = self.extract_street_name(body_text)
                        if street_text and not self.proper_street(street_text):
                            continue

                        if not self.has_garden_in_desc(body_text):
                            continue

                        title = detail_soup.find("h4", class_="css-10ofhqw").text
                        price = self.extract_price(detail_soup.find("h3", class_="css-fqcbii").text) if detail_soup.find("h3", class_="css-fqcbii") else 0

                        details_block = detail_soup.find_all("p", class_="css-1los5bp")
                        details_text = " ".join(p.text for p in details_block)
                        area = self.extract_surface(details_text)
                        floor = self.extract_floor(details_text)

                        price_per_m = price / area if area else 0

                        if area and (area < self.min_area or area > self.max_area):
                            continue
                        if floor > self.parter:
                            continue
                        if price_per_m > self.max_on_meter:
                            continue

                        offer = {
                            "url": link,
                            "tytul": title,
                            "cena": price,
                            "powierzchnia": area,
                            "na_metr": round(price_per_m),
                            "zrodlo": self.src,
                            "data_dodania": self.date_now(),
                            "fav": '0',
                            "hide": '0'
                        }
                        offers.append(offer)
                        save_offer_backup(offer, self.src + ".csv")
                        time.sleep(0.5)
                    except:
                        print(f'[{self.src}] błąd podczas sprawdzania oferty: {link}')
                last_real_page = page
                page += 1
        finally:
            self.driver.quit()

        self.cleanup(user_data_dir)

        self.log()
        return offers

    def extract_street_name(self, text: str) -> str | None:
        matches = re.findall(r'ul\.?\s+([A-ZĄĆĘŁŃÓŚŹŻ][\wąćęłńóśźż\-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż0-9/]+)*)', text)

        # Zwróć pierwszy dopasowany wynik
        return matches[0] if matches else None

    def extract_surface(self, text):
        match = re.search(r"Powierzchnia:\s*([\d,.]+)", text)
        if match:
            # Zamieniamy przecinki na kropki i konwertujemy na float
            val = match.group(1).replace(',', '.')
            return float(val)
        return 0

    def extract_floor(self, text):
        match = re.search(r"Poziom:\s*([0-9]+)", text)
        if match:
            return int(match.group(1))
        return 999  # Można też zwrócić np. None, jeśli nie znaleziono


    def init_driver(self, user_data_dir):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        print("Using Chrome profile at:", user_data_dir)
        options.add_argument(f"--user-data-dir={user_data_dir}")

        driver = webdriver.Chrome(options=options)
        return driver

    def cleanup(self, user_data_dir):
        # Usuwamy tymczasowy katalog profilu po zakończeniu pracy
        shutil.rmtree(user_data_dir, ignore_errors=True)

    def scroll_to_load_all(self, step=200, pause=0.5, max_wait=5):
        import time

        last_height = 0
        while True:
            current_height = self.driver.execute_script("return document.body.scrollHeight")

            for y in range(last_height, current_height, step):
                self.driver.execute_script(f"window.scrollTo(0, {y});")
                time.sleep(pause)

            # Czekamy dodatkowo na ostatnie doładowania
            time.sleep(max_wait)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == current_height:
                break

            last_height = current_height


    def get_page_number_from_url(self, url):
        parsed_url = urlparse(url)
        page = parse_qs(parsed_url.query).get('page', [None])[0]
        return int(page) if page else None
