import feedparser
import json
import datetime
import csv
from urllib.parse import quote

today = datetime.date.today()

signals = []

with open("competitors.csv") as f:

    reader = csv.DictReader(f)

    for row in reader:

        company = row["company"]
        query = row["query"]

        print(f"Checking news for {company}")

        encoded_query = quote(query)

        feed_url = f"https://news.google.com/rss/search?q={encoded_query}+energy+trading"

        data = feedparser.parse(feed_url)

        for entry in data.entries[:5]:

            signals.append({
                "company": company,
                "date": str(today),
                "text": entry.title,
                "source": "news"
            })


try:

    with open("signals.json") as f:
        existing = json.load(f)

except:

    existing = []


all_signals = existing + signals


with open("signals.json", "w") as f:

    json.dump(all_signals, f, indent=2)


print(f"Added {len(signals)} signals")
