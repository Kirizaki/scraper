import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from csv_writer import init_csv, is_offer_saved, remove_duplicates, save_offer
from scrapers.otodom_scraper import OtodomScraper
from scrapers.olx_scraper import OlxScraper
from scrapers.gratka_scraper import GratkaScraper
from scrapers.morizon_scraper import MorizonScraper
from scrapers.adresowo_scraper import AdresowoScraper
import time

def process_scraper(scraper_cls):
    scraper = scraper_cls()
    return scraper.scrape()

def main():
    start = time.time()
    init_csv()

    # scrapers = [MorizonScraper, OlxScraper, GratkaScraper, MorizonScraper, AdresowoScraper, OtodomScraper]
    scrapers = [OtodomScraper]

    offers_all = []
    with ThreadPoolExecutor(max_workers=len(scrapers)) as executor:
        futures = [executor.submit(process_scraper, scraper_cls) for scraper_cls in scrapers]
        for future in as_completed(futures):
            try:
                offers = future.result()
                offers_all.extend(offers)
            except Exception as e:
                print(f"⚠️ Błąd w jednym ze scraperów: {e}")

    new_count = 0
    for offer in offers_all:
        if not is_offer_saved(offer["url"]):
            offer["data_dodania"] = datetime.now().strftime("%H:%M-%d-%m-%Y")
            save_offer(offer)
            print(f"✅ Zapisano nową ofertę: {offer['url']}")
            new_count += 1

    if new_count > 0:
        with open('notify.flag', 'w') as f:
            f.write('yes')
            remove_duplicates()
    else:
        if os.path.exists('notify.flag'):
            os.remove('notify.flag') 

    elapsed = time.time() - start
    print(f"⏱️ Skrypt wykonał się w {elapsed:.2f} sekund.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    main()