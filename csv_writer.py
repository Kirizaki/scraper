import csv
import os
import threading
import shutil
from datetime import datetime

FIELDNAMES = ["url", "tytul", "cena", "powierzchnia", "na_metr", "zrodlo", "data_dodania", "fav", "hide"]
CSV_FILE = 'wyniki.csv'
BACKUP_DIR = "backup"

# Blokada, aby synchronizować dostęp do pliku CSV
csv_lock = threading.Lock()

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def save_offer(offer: dict):
    with csv_lock:  # Blokujemy dostęp do zapisu w pliku CSV
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow(offer)

def save_offer_backup(offer: dict, filename: str):
    with csv_lock:  # Blokujemy dostęp do zapisu w pliku CSV
        if not offer or not filename:
            return
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow(offer)

def is_offer_saved(url: str) -> bool:
    # TODO: Duplicates due to different postfix in url:
    # https://obido.pl/rynek-pierwotny-trojmiasto/kusocinskiego/mieszkanie-c_89.html#from_search_2,Kusocińskiego Budynek A,815925,64,12748,obido,08:19-20-05-2025,0,1
    # https://obido.pl/rynek-pierwotny-trojmiasto/kusocinskiego/mieszkanie-a_07.html#from_search_10,Kusocińskiego Budynek A,946964,78,12140,obido,08:19-20-05-2025,0,1
    # https://obido.pl/rynek-pierwotny-trojmiasto/kusocinskiego/mieszkanie-c_89.html#from_search_3,Kusocińskiego Budynek A,815925,64,12748,obido,10:25-20-05-2025,0,0
    # https://obido.pl/rynek-pierwotny-trojmiasto/kusocinskiego/mieszkanie-a_07.html#from_search_1,Kusocińskiego Budynek A,946964,78,12140,obido,10:25-20-05-2025,0,0
    if not os.path.exists(CSV_FILE):
        return False
    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return any(row["url"] == url for row in reader)

def remove_duplicates():
    with csv_lock:  # Blokujemy dostęp do zapisu w pliku CSV
        seen = set()
        unique_rows = []

        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            for row in reader:
                row_tuple = tuple(row)
                if row_tuple not in seen:
                    seen.add(row_tuple)
                    unique_rows.append(row)

        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(unique_rows)

def backup_csv():
    with csv_lock:
        if not os.path.exists(CSV_FILE):
            return

        # Upewnij się, że katalog backup istnieje
        os.makedirs(BACKUP_DIR, exist_ok=True)

        # Stwórz nazwę pliku z timestampem
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"{BACKUP_DIR}/wyniki_{timestamp}.csv"

        shutil.copy2(CSV_FILE, backup_filename)
        print(f"📦 Backup zapisany: {backup_filename}")
