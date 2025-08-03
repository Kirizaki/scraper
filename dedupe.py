# dedupe.py

import csv
import sys
import os
import shutil
from datetime import datetime

INPUT_FILE = 'wyniki.csv'
BACKUP_FILE = f'wyniki_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

def normalize_url(url):
    # Only strip /hpr from otodom.pl URLs
    if 'otodom.pl/hpr/' in url:
        return url.replace('/hpr', '')
    return url

def backup_input_file():
    if os.path.exists(INPUT_FILE):
        shutil.copy(INPUT_FILE, BACKUP_FILE)
        print(f"Backup created: {BACKUP_FILE}")
    else:
        print(f"Input file '{INPUT_FILE}' not found.")
        exit(1)

def main():
    seen = set()
    unique_rows = []

    with open(INPUT_FILE, newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for row in reader:
            norm_url = normalize_url(row[0])
            if norm_url not in seen:
                seen.add(norm_url)
                unique_rows.append(row)

    with open(INPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(unique_rows)

    print(f"Deduplicated rows written to {INPUT_FILE} ({len(unique_rows)} unique rows).")

if __name__ == "__main__":
    main()
