from abc import ABC, abstractmethod
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import re
from csv_writer import save_offer_backup

# TODO:
# 1. Filtrować po pietrze, czyli PARTER! (otodom: DONE!)
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
### WSZYSTKO DONE DLA OTODOM!
class RealEstateScraper(ABC):
    def __init__(self) -> None:
        self.counter = 0
        self.src = '..'
        self.keywords = ["ogród", "ogrod", "ogrodek", "ogródek", "z ogrodem", "dostęp do ogrodu", "dostep do ogrodu"]
        self.max_on_meter = 17000
        self.min_area = 50
        self.max_area = 125
        self.parter = 0

    def extract_surface(self, text):
        # Zlokalizuj fragment po "powierzchnia"
        match = re.search(r'powierzchnia\s*([\d\s,.]+)\s*m²', text.lower())
        if match:
            val = match.group(1)
            # Usuń spacje i zamień przecinek na kropkę (dla liczb z , zamiast .)
            cleaned = val.replace(' ', '').replace(',', '.')
            try:
                return float(cleaned)
            except ValueError:
                return 0
        return 0

    @abstractmethod
    def scrape(self) -> list[dict]:
        """Zwraca listę ofert jako słowniki."""
        pass

    def has_garden_in_additional_info(self, informacje_dodatkowe):
        for info in informacje_dodatkowe:
            for word in self.keywords:
                return word in info.text

        return False

    def has_garden_in_desc(self, opis):
        for word in self.keywords:
            return word in opis

        return False

    def date_now(self):
        # Pobranie bieżącej daty i godziny
        now = datetime.now()
        return now.strftime("%H:%M-%d-%m-%Y")  # Format: godzina:minuta-dzień-miesiąc-rok

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

    def has_street(self, street_text):
        keywords = ['ul.', 'ulica']
        for word in keywords:
            if word in street_text:
                return True

        return False

    def proper_street(self, street_text):
        keywords = ['Józefa Hallera', 'Hallera', 'Tadeusza Kościuszki', 'Kościuszki', 'Kosciuszki', 'Sochaczewska', 'Żywiecka', 'Zywiecka' 'Legionów', 'Legionow']
        for word in keywords:
            if word in street_text:
                return False

        return True

    def extract_floor(self, text):
        import re

        # Słownik liczebników porządkowych
        słowne_piętra = {
            "parter": 0,
            "pierwsze": 1,
            "drugie": 2,
            "trzecie": 3,
            "czwarte": 4,
            "piąte": 5,
            "piate": 5,
            "szóste": 6,
            "szoste": 6,
            "siódme": 7,
            "siodme": 7,
            "ósme": 8,
            "osme": 8,
            "dziewiąte": 9,
            "dziewiate": 9,
            "dziesiąte": 10,
            "dziesiate": 10
        }

        # Normalizacja
        text = text.lower()

        # Najpierw spróbuj znaleźć format typu "Piętro 3" albo "Piętro 1/3"
        match = re.search(r'pi[eę]tro\s*([0-9]+)(?:/[0-9]+)?', text)
        if match:
            return int(match.group(1))

        # Sprawdź czy występuje słowo "parter"
        if "parter" in text:
            return 0

        # Spróbuj znaleźć liczebnik słowny
        for slowo, wartosc in słowne_piętra.items():
            if slowo in text:
                return wartosc

        return 999

    def extract_price(self, text):
        # Usuń wszystkie znaki niebędące cyframi
        numeric_str = re.sub(r'\D', '', text)
        return float(numeric_str) if numeric_str else None