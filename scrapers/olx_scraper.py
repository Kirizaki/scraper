import requests, re, time
from bs4 import BeautifulSoup
from csv_writer import save_offer_backup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden

BASE_URL = "https://www.olx.pl"

class OlxScraper(RealEstateScraper):
    def scrape(self):
        self.src = 'olx'
        page = 1
        while True:
            search_url = BASE_URL + f"/nieruchomosci/mieszkania/sprzedaz/gdansk/?page={page}&search%5Bdistrict_id%5D=99&search%5Border%5D=created_at%3Adesc"
            res = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
            real_page = self.get_page_number(res.url)
            if not real_page or int(real_page) < page:
                break

            print(f"\n   [{self.src}] przeszukuje stronę (#{page}): {search_url}")
            soup = BeautifulSoup(res.text, 'html.parser')
            links = {BASE_URL + a['href'].split('?')[0] for a in soup.find_all('a', href=True) if re.match(r"^/d/oferta/[^/]+\.html", a['href'])}

            offers = []
            for link in links:
                try:
                    self.counter += 1
                    res = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
                    soup = BeautifulSoup(res.text, 'html.parser')
                    title = 'brak'
                    for header in soup.find_all("h4"):
                        if header.attrs.get('class')[0] == "css-10ofhqw":
                            title = header.text.strip()
                    price = soup.find("h3", class_="css-fqcbii").text.strip()
                    body = soup.get_text(separator=' ', strip=True)
                    garden, snippet = has_garden(body)
                    area_val = "brak"
                    for p in soup.find_all("p", class_="css-1los5bp"):
                        if "powierzchnia" in p.text.lower():
                            area_val = p.text.strip()
                    if garden:
                        offer = {
                            "url": link,
                            "tytul": title,
                            "dzielnica": "Wrzeszcz",
                            "cena": price,
                            "powierzchnia": area_val,
                            "ogrod_fragment": snippet,
                            "zrodlo": "olx",
                            "data_dodania": self.date_now(),
                            "fav": '',
                            "hide": ''
                        }
                        offers.append(offer)
                        save_offer_backup(offer, self.src+".csv")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"❌ Error: {e}")
            page += 1

        self.log()
        return offers
