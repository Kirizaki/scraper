import csv
from pathlib import Path

OUTPUT_FILE = "merged.csv"

def merge_all_csvs_by_url():
    csv_files = list(Path(".").glob("*.csv"))
    merged = {}

    for file in csv_files:
        if file.name == OUTPUT_FILE:
            continue  # pomiń plik wyjściowy, jeśli istnieje

        with file.open(newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or not row[0].strip().startswith("http"):
                    continue  # pomiń niepoprawne lub puste wiersze
                url = row[0].strip()
                if url not in merged:
                    merged[url] = row

    with open(OUTPUT_FILE, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in merged.values():
            writer.writerow(row)

    print(f"✅ Zmergowano {len(csv_files)} plików -> {OUTPUT_FILE}")
    print(f"📦 Unikalnych ofert: {len(merged)}")

if __name__ == "__main__":
    merge_all_csvs_by_url()
