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
        blog = row["blog"]

        print(f"Checking blog for {company}")

        r = requests.get(blog, headers=headers)

        soup = BeautifulSoup(r.text, "html.parser")

        articles = soup.find_all("a")

        for a in articles[:5]:

            title = a.get_text(strip=True)

            if len(title) > 40:

                signals.append({
                    "company": company,
                    "date": str(today),
                    "text": title,
                    "source": "blog"
                })

try:
    with open("signals.json") as f:
        existing = json.load(f)
except:
    existing = []

with open("signals.json","w") as f:
    json.dump(existing + signals,f,indent=2)
