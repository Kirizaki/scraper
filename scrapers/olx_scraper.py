from abc import ABC, abstractmethod
import random
import time
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import shutil
import requests, re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tempfile
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from scraper_base import RealEstateScraper
from csv_writer import save_offer_backup

BASE_URL = "https://www.olx.pl"

class OlxScraper(RealEstateScraper):
    def __init__(self) -> None:
        super().__init__()
        self._current_page = 0
        self._loaded_page = self._current_page
        self.src = 'olx'

    def scrape(self):
        offers = []
        # TODO: Playwright!
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                locale="en-US"
            )
            page = context.new_page()

            # debug
            # counter = 0
            last_real_page = self._current_page
            while True:
                try:
                    # while counter < 1:  # debug
                    listing_url = self.build_listing_url(self._current_page + 1)
                    page.goto(listing_url)
                    self.human_delay()
                    self.scroll_to_load_all(page)

                    content = BeautifulSoup(page.content(), "html.parser")

                    current_page_tag = content.find("li", class_="pagination-item__active")
                    if current_page_tag is not None:
                        current_page = int(current_page_tag.text.strip())
                    else:
                        current_page = None
                    if current_page is None or current_page <= last_real_page:
                        print(f"\t   [{self.src}]Osiągnięto koniec listy ofert.")
                        break
                    print(f"\n   [{self.src}] przeszukuje stronę (#{current_page}): {listing_url}")
                    self.human_delay()
                    articles = content.find_all("a", class_="css-1tqlkj0")
                    # for article in articles:
                    for article in articles:
                        offer_url = article.get('href')
                        if "https://" in offer_url:
                            continue
                        link = self.build_offer_url(offer_url)
                        page.goto(link)
                        self.human_delay()
                        # self.scroll_to_load_all(page, max_wait=5)
                        content = BeautifulSoup(page.content(), "html.parser")
                        if not self.check_address(content.find_all("a", class_="css-tyi2d1")):
                            continue
                        offer = {
                            "url": link,
                            "tytul": 'title',
                            "cena": 'cena',
                            "powierzchnia": 'area',
                            "na_metr": 'm2',
                            "zrodlo": self.src,
                            "data_dodania": self.date_now(),
                            "fav": '0',
                            "hide": '0'
                        }
                        self.counter += 1
                        offers.append(offer)
                        save_offer_backup(offer, self.src+".csv")
                        continue

                        # TODO: Playwright!
                    last_real_page = self._current_page
                    self._current_page += 1
                except Exception as e:
                    print(f"\n   [{self.src}] błąd podczas sprawdzania oferty: {link}\nerror:\n{e}")

            browser.close()

        return offers
        #     try:
        #         self.src = 'olx'
        #         offers = []
        #         page = 0
        #         last_real_page = None
        #         while True:
        #             url = f"https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/gdansk/?page={page}&search%5Bdistrict_id%5D=99&search%5Border%5D=created_at%3Adesc"
        #             self.driver.get(url)
        #             self.scroll_to_load_all()
        #             soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        #             # Wyciągamy numer strony z URL
        #             current_page_tag = soup.find("li", class_="pagination-item__active")
        #             if current_page_tag is not None:
        #                 current_page = int(current_page_tag.text.strip())
        #             else:
        #                 current_page = None
        #             if current_page is None or current_page < page or current_page == last_real_page:
        #                 print(f"\t   [{self.src}]Osiągnięto koniec listy ofert.")
        #                 break

        #             print(f"\n   [{self.src}] przeszukuje stronę (#{page}): {self.driver.current_url}")

        #             link_elements = soup.find_all("a", class_="css-1tqlkj0")
        #             print(f"\n   [{self.src}]🔗 Znaleziono {len(link_elements)} ofert po pełnym scrollu.")
        #             link = 'pierwszy_link'
        #             for link_element in link_elements:
        #                 if 'otodom.pl' in link_element.get("href"):
        #                     continue

        #                 link = f'{BASE_URL}{link_element.get("href")}'
        #                 try:
        #                     self.counter += 1
        #                     detail_res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
        #                     detail_soup = BeautifulSoup(detail_res.text, "html.parser")

        #                     body_text = detail_soup.get_text(separator=' ', strip=True)
        #                     if "wrzeszcz" not in body_text.lower():
        #                         continue

        #                     street_text = self.extract_street_name(body_text)
        #                     if street_text and not self.proper_street(street_text):
        #                         continue

        #                     if not self.has_garden_in_desc(body_text):
        #                         continue

        #                     title = detail_soup.find("h4", class_="css-10ofhqw").text
        #                     price = self.extract_price(detail_soup.find("h3", class_="css-fqcbii").text) if detail_soup.find("h3", class_="css-fqcbii") else 0

        #                     details_block = detail_soup.find_all("p", class_="css-1los5bp")
        #                     details_text = " ".join(p.text for p in details_block)
        #                     area = self.extract_surface(details_text)
        #                     floor = self.extract_floor(details_text)

        #                     price_per_m = price / area if area else 0

        #                     if area and (area < self.min_area or area > self.max_area):
        #                         continue
        #                     if floor > self.parter:
        #                         continue
        #                     if price_per_m > self.max_on_meter:
        #                         continue

        #                     offer = {
        #                         "url": link,
        #                         "tytul": title,
        #                         "cena": int(price),
        #                         "powierzchnia": int(area),
        #                         "na_metr": int(price_per_m),
        #                         "zrodlo": self.src,
        #                         "data_dodania": self.date_now(),
        #                         "fav": '0',
        #                         "hide": '0'
        #                     }
        #                     offers.append(offer)
        #                     save_offer_backup(offer, self.src + ".csv")
        #                     time.sleep(0.5)
        #                 except:
        #                     print(f"\n   [{self.src}] błąd podczas sprawdzania oferty: {link}")
        #             last_real_page = page
        #             page += 1
        #     finally:
        #         self.driver.quit()

        # self.cleanup(user_data_dir)

        # self.log()
        # return offers

    def check_address(self, elements):
        for el in elements:
            district = el.text.strip().lower()
            if "wrzeszcz" in district or "oliwa" in district:
                return True
        return False

    def build_listing_url(self, page: int) -> str:
        return f"https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/gdansk/?page={page}&search%5Bfilter_enum_floor_select%5D%5B0%5D=floor_0&search%5Bfilter_enum_floor_select%5D%5B1%5D=floor_1&search%5Bfilter_enum_market%5D%5B0%5D=secondary&search%5Bfilter_float_m%3Ato%5D=120&search%5Bfilter_float_price_per_m%3Ato%5D=16000&search%5Border%5D=created_at%3Adesc"

    def build_offer_url(self, offer_url: str):
        return f"{BASE_URL}{offer_url}"


    def human_delay(self, min_ms=300, max_ms=1200):
        """Waits a random human-like delay between actions"""
        delay = random.uniform(min_ms, max_ms) / 1000  # ms to seconds
        time.sleep(delay)

    def _update_loaded_page_number(self, url: str):
        try:
            self._loaded_page = self._get_loaded_page_number(url)
        except Exception as e:
            print(f"Error on getting loaded page number: {e}")
            return False

    def _get_loaded_page_number(self, url):
        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        return int(query.get("page", [None])[0]) if "page" in query else None

    def _is_end(self):
        return self._loaded_page < self._current_page

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

    def scroll_to_load_all(self, page, step=200, pause=0.5, max_wait=15):
        """
        Scrolls down the page step-by-step to trigger lazy-loading content, 
        imitating human scrolling behavior.

        Args:
            step (int): How many pixels to scroll each step.
            pause (float): Pause (in seconds) between scroll steps.
            max_wait (float): Maximum time (in seconds) to wait at the bottom before stopping.
        """
        prev_height = -1
        same_height_duration = 0
        start_time = time.time()

        while True:
            current_height = page.evaluate("document.body.scrollHeight")
            if current_height == prev_height:
                same_height_duration = time.time() - start_time
                if same_height_duration >= max_wait:
                    break
            else:
                same_height_duration = 0
                start_time = time.time()

            page.evaluate(f"window.scrollBy(0, {step});")
            time.sleep(pause)
            prev_height = current_height


    def get_page_number_from_url(self, url):
        parsed_url = urlparse(url)
        page = parse_qs(parsed_url.query).get('page', [None])[0]
        return int(page) if page else None
