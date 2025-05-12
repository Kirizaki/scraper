import csv
import os
import threading

FIELDNAMES = ['url', 'tytul', 'dzielnica', 'cena', 'powierzchnia', 'ogrod_fragment', 'zrodlo', 'data_dodania','fav', 'hide']
CSV_FILE = 'wyniki.csv'

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

remove_duplicates()