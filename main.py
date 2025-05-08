import concurrent.futures
from scrapers.otodom_scraper import OtodomScraper
from scrapers.olx_scraper import OlxScraper
from csv_writer import init_csv, save_offer
import threading

def main():
    init_csv()
    scrapers = [OtodomScraper(), OlxScraper()]

    # Tworzymy blokadę do synchronizacji dostępu do pliku CSV
    csv_lock = threading.Lock()

    def save_offers_concurrently(scraper):
        offers = scraper.scrape()
        with csv_lock:  # Zabezpieczamy dostęp do pliku CSV
            for offer in offers:
                save_offer(offer)
                print(f"✅ Zapisano: {offer['url']}")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(save_offers_concurrently, scraper) for scraper in scrapers]
        
        # Czekamy na zakończenie wszystkich wątków
        for future in concurrent.futures.as_completed(futures):
            future.result()

if __name__ == "__main__":
    main()
