from scrapers.otodom_scraper import OtodomScraper
from scrapers.olx_scraper import OlxScraper
from csv_writer import init_csv, is_offer_saved, save_offer
from datetime import datetime

def main():
    init_csv()
    scrapers = [OtodomScraper(), OlxScraper()]
    
    for scraper in scrapers:
        offers = scraper.scrape()
        new_count = 0
        for offer in offers:
            if not is_offer_saved(offer["url"]):
                offer["data_dodania"] = datetime.now().strftime("%H:%M-%d-%m-%Y")
                save_offer(offer)
                print(f"✅ Zapisano nową ofertę: {offer['url']}")
                new_count += 1

        # Zapisz flagę do pliku – wykorzystywane przez GitHub Actions
        with open("notify.flag", "w") as f:
            f.write("yes" if new_count > 0 else "no")

if __name__ == "__main__":
    main()
