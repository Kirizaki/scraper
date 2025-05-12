from abc import ABC, abstractmethod
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from csv_writer import save_offer_backup

# TODO:
# 1. Filtrować po pietrze, czyli PARTER!
# 2. Odpadają ulice:
#   al. gen. Józefa Hallera
#   Tadeusza Kościuszki
#   Sochaczewska
#   Żywiecka
#   Legionów
  
# 3. Powierzchnia 55m2 - 120m2
# 4. Max za 1m2: 16.000
# 5. Sprawdzic duplikaty jeszcze raz:
# https://www.otodom.pl/hpr/pl/oferta/ogrod-miejsce-naziemne-pracownia-kancelaria-ID4tO7D
# 6. 
class RealEstateScraper(ABC):
    def __init__(self) -> None:
        self.counter = 0
        self.src = '..'

    @abstractmethod
    def scrape(self) -> list[dict]:
        """Zwraca listę ofert jako słowniki."""
        pass

    def date_now(self):
        # Pobranie bieżącej daty i godziny
        now = datetime.now()
        return now.strftime("%H-%d-%m-%Y")  # Format: godzina-dzień-miesiąc-rok

    def backup(self, offers):
        if not offers:
            return

        print(f"\n   [{offers[0]['zrodlo']}] nowych ofert: {len(offers)}")
        for offer in offers:
            save_offer_backup(offer, self.src+".csv")

    def log(self):
        print(f"\n   [{self.src}] sprawdzonych ofert: {self.counter}")

    def get_page_number(self, url: str) -> int:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        page = query_params.get('page', ['1'])[0]  # domyślnie strona 1
        return int(page)