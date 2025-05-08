from abc import ABC, abstractmethod
from datetime import datetime

class RealEstateScraper(ABC):
    @abstractmethod
    def scrape(self) -> list[dict]:
        """Zwraca listę ofert jako słowniki."""
        pass

    def date_now(self):
        # Pobranie bieżącej daty i godziny
        now = datetime.now()
        return now.strftime("%H-%d-%m-%Y")  # Format: godzina-dzień-miesiąc-rok
