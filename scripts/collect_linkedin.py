import requests
from bs4 import BeautifulSoup
import csv
import json
import datetime

today = datetime.date.today()

signals = []

headers = {"User-Agent": "Mozilla/5.0"}

with open("competitors.csv") as f:

    reader = csv.DictReader(f)

    for row in reader:

        company = row["company"]
        url = row["linkedin"]

        print(f"Checking LinkedIn for {company}")

        r = requests.get(url, headers=headers)

        soup = BeautifulSoup(r.text, "html.parser")

        texts = soup.find_all("span")

        for t in texts:

            text = t.get_text(strip=True)

            if len(text) > 80:

                signals.append({
                    "company": company,
                    "date": str(today),
                    "text": text,
                    "source": "linkedin"
                })

try:
    with open("signals.json") as f:
        existing = json.load(f)
except:
    existing = []

with open("signals.json","w") as f:
    json.dump(existing + signals,f,indent=2)
