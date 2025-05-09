import requests, re, time
from bs4 import BeautifulSoup
from scraper_base import RealEstateScraper
from utils.garden_utils import has_garden
from csv_writer import is_offer_saved

BASE_URL = "https://www.olx.pl"
SEARCH_URL = BASE_URL + "/nieruchomosci/mieszkania/sprzedaz/gdansk/?search%5Bdistrict_id%5D=99"

class OlxScraper(RealEstateScraper):
    def scrape(self):
        res = requests.get(SEARCH_URL, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        links = {BASE_URL + a['href'].split('?')[0] for a in soup.find_all('a', href=True) if re.match(r"^/d/oferta/[^/]+\.html", a['href'])}

        offers = []
        for link in links:
            try:
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
                    offers.append({
                        "url": link,
                        "title": title,
                        "dzielnica": "Wrzeszcz",
                        "cena": price,
                        "powierzchnia": area_val,
                        "ogrod_fragment": snippet,
                        "zrodlo": "olx",
                        "data_dodania": super().date_now()
                    })
                time.sleep(0.5)
            except Exception as e:
                print(f"❌ Error: {e}")
        return offers