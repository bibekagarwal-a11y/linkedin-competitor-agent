import feedparser
import csv
import json
import datetime

today = datetime.date.today()

posts = []

# Read competitors
with open("competitors.csv") as f:
    reader = csv.DictReader(f)

    for row in reader:

        company = row["company"]
        url = row["linkedin"]

        print(f"Checking posts for {company}")

        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:

            post = {
                "company": company,
                "date": str(today),
                "text": entry.title,
                "url": entry.link
            }

            posts.append(post)

# Load existing posts
try:
    with open("posts.json") as f:
        existing_posts = json.load(f)
except:
    existing_posts = []

# Safe duplicate detection
existing_urls = {p.get("url") for p in existing_posts if "url" in p}

new_posts = [p for p in posts if p["url"] not in existing_urls]

all_posts = existing_posts + new_posts

with open("posts.json", "w") as f:
    json.dump(all_posts, f, indent=2)

print(f"Added {len(new_posts)} new posts")
