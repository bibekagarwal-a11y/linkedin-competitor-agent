import feedparser
import json
import datetime
import csv

today = datetime.date.today()

signals = []

with open("competitors.csv") as f:
    reader = csv.DictReader(f)

    for row in reader:

        company = row["company"]

        feed = f"https://news.google.com/rss/search?q={company}"

        data = feedparser.parse(feed)

        for e in data.entries[:5]:

            signals.append({
                "company": company,
                "date": str(today),
                "text": e.title,
                "source": "news"
            })

try:
    with open("signals.json") as f:
        existing = json.load(f)
except:
    existing = []

all_signals = existing + signals

with open("signals.json","w") as f:
    json.dump(all_signals,f,indent=2)
