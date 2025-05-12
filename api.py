from flask import Flask, jsonify, request, send_from_directory
import csv
import os

app = Flask(__name__)

CSV_FILE = 'wyniki.csv'
FIELDS = [
    "url", "tytul", "dzielnica", "cena", "powierzchnia",
    "ogrod_fragment", "zrodlo", "data_dodania", "fav", "hide"
]

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/get-data')
def get_data():
    data = []
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            for field in FIELDS:
                row.setdefault(field, '0')
            data.append(row)
    return jsonify(data)

@app.route('/update-fav', methods=['POST'])
def update_fav():
    req = request.get_json()
    url = req.get('url')
    fav = req.get('fav')

    rows = []
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            if row['url'] == url:
                row['fav'] = fav
            rows.append(row)

    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    return '', 204

@app.route('/update-hide', methods=['POST'])
def update_hide():
    req = request.get_json()
    url = req.get('url')

    rows = []
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            if row['url'] == url:
                row['hide'] = '1'
            rows.append(row)

    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    return '', 204

if __name__ == '__main__':
    app.run(debug=True, port=5555)
