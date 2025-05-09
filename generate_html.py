import csv
import re
from datetime import datetime

CSV_FILE = 'wyniki.csv'
HTML_FILE = 'wyniki.html'

def generate_html(csv_file, html_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write("""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Oferty mieszkań</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2rem; background: #f8f8f8; }
        table { width: 100%; border-collapse: collapse; background: white; }
        th, td { padding: 10px; border: 1px solid #ccc; text-align: left; }
        th { background: #f0f0f0; cursor: pointer; }
        tr:hover { background: #f9f9f9; }
        caption { caption-side: top; font-size: 1.5rem; margin-bottom: 1rem; }
    </style>
</head>
<body>
    <table id="ofertyTable">
        <caption>Oferty mieszkań – wygenerowano: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """</caption>
        <thead>
            <tr>
""")
        for field in reader.fieldnames:
            f.write(f'                <th onclick="sortTable(this)">{field}</th>\n')
        f.write("""            </tr>
        </thead>
        <tbody>
""")
        for row in rows:
            f.write("            <tr>\n")
            for field in reader.fieldnames:
                value = row[field]
                if field == "url":
                    value = f'<a href="{value}" target="_blank">Link</a>'
                elif field.lower().startswith("data") or re.match(r'^\d{1,2}(:\d{2})?-\d{2}-\d{2}-\d{4}$', value):
                    # Dodaj ":00" jeśli nie ma minut
                    if re.match(r'^\d{1,2}-\d{2}-\d{2}-\d{4}$', value):
                        hour, day, month, year = value.split('-')
                        value = f'{hour}:00-{day}-{month}-{year}'
                f.write(f'                <td>{value}</td>\n')
            f.write("            </tr>\n")
        f.write("""        </tbody>
    </table>
    <script>
    function sortTable(header) {
        const table = header.closest('table');
        const index = Array.from(header.parentNode.children).indexOf(header);
        const rows = Array.from(table.tBodies[0].rows);
        const asc = !header.classList.contains('asc');
        for (let th of header.parentNode.children) th.classList.remove('asc', 'desc');
        header.classList.toggle(asc ? 'asc' : 'desc', true);

        const isDateLike = text => /^\d{1,2}(:\d{2})?-\d{2}-\d{2}-\d{4}$/.test(text);

        const parseDate = (str) => {
            const parts = str.split('-');
            let timePart = parts[0];
            const day = parts[1];
            const month = parts[2];
            const year = parts[3];

            // If time includes minutes
            let [hour, minute] = timePart.includes(':') ? timePart.split(':') : [timePart, '00'];
            return new Date(`${year}-${month}-${day}T${hour.padStart(2, '0')}:${minute}`);
        };

        rows.sort((a, b) => {
            let cellA = a.cells[index].innerText.trim();
            let cellB = b.cells[index].innerText.trim();

            if (isDateLike(cellA) && isDateLike(cellB)) {
                const dateA = parseDate(cellA);
                const dateB = parseDate(cellB);
                return asc ? dateA - dateB : dateB - dateA;
            }

            return asc
                ? cellA.localeCompare(cellB, 'pl', { numeric: true })
                : cellB.localeCompare(cellA, 'pl', { numeric: true });
        });

        for (let row of rows) table.tBodies[0].appendChild(row);
    }
    </script>
</body>
</html>
""")

if __name__ == "__main__":
    generate_html(CSV_FILE, HTML_FILE)
