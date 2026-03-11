import requests
from bs4 import BeautifulSoup
import json
import datetime
import csv

today = datetime.date.today()

headers = {"User-Agent": "Mozilla/5.0"}

posts = []

with open("competitors.csv") as f:
    reader = csv.DictReader(f)

    for row in reader:

        company = row["company"]
        url = row["linkedin"]

        print(f"Checking {company}")

        try:

            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")

            texts = soup.find_all("span")

            for t in texts:

                text = t.get_text(strip=True)

                if len(text) > 60:

                    posts.append({
                        "company": company,
                        "date": str(today),
                        "text": text
                    })

        except Exception as e:
            print(e)


try:
    with open("posts.json") as f:
        existing = json.load(f)
except:
    existing = []

existing_texts = {p["text"] for p in existing if "text" in p}

new_posts = [p for p in posts if p["text"] not in existing_texts]

all_posts = existing + new_posts

with open("posts.json","w") as f:
    json.dump(all_posts,f,indent=2)

print(f"Added {len(new_posts)} signals")
