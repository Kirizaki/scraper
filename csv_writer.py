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

from urllib.parse import urlparse

def strip_url_fragment(url: str) -> str:
    return url.split('#')[0]

def is_offer_saved(url: str) -> bool:
    if "obido" in url:
        base_url = strip_url_fragment(url)
    else:
        base_url = url

    if not os.path.exists(CSV_FILE):
        return False

    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "obido" in url:
                raw_url = row["url"]
                saved_base_url = strip_url_fragment(row["url"])
            else:
                saved_base_url = raw_url
            if saved_base_url == base_url:
                return True
    return False

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
