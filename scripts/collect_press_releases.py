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
        press = row["press"]

        print(f"Checking press releases for {company}")

        r = requests.get(press, headers=headers)

        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.find_all("a")

        for i in items[:5]:

            title = i.get_text(strip=True)

            if len(title) > 40:

                signals.append({
                    "company": company,
                    "date": str(today),
                    "text": title,
                    "source": "press"
                })

try:
    with open("signals.json") as f:
        existing = json.load(f)
except:
    existing = []

with open("signals.json","w") as f:
    json.dump(existing + signals,f,indent=2)
