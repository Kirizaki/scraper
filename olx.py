import os
from datetime import datetime
from csv_writer import init_csv, is_offer_saved, remove_duplicates, save_offer
from scrapers.olx_scraper import OlxScraper
import time

def process_scraper(scraper_cls):
    scraper = scraper_cls()
    return scraper.scrape()

def main():
    start = time.time()
    init_csv()

    olx = OlxScraper()

    offers_all = []
    offers_all = olx.scrape()
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