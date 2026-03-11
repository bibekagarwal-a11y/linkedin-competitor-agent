import feedparser
import json
import datetime
import csv

today = datetime.date.today()
cutoff = today - datetime.timedelta(days=30)

posts = []

with open("competitors.csv") as f:
    reader = csv.DictReader(f)

    for row in reader:

        company = row["company"]
        company_url = row["linkedin"]

        print(f"Checking news for {company}")

        search = company.replace(" ", "+")
        feed_url = f"https://news.google.com/rss/search?q={search}"

        feed = feedparser.parse(feed_url)

        for entry in feed.entries:

            try:
                published = datetime.datetime(*entry.published_parsed[:6]).date()
            except:
                continue

            if published < cutoff:
                continue

            post = {
                "company": company,
                "company_url": company_url,
                "date": str(published),
                "text": entry.title,
                "url": entry.link,
                "source": "news"
            }

            posts.append(post)


# Load existing posts
try:
    with open("posts.json") as f:
        existing = json.load(f)
except:
    existing = []

existing_urls = {p["url"] for p in existing if "url" in p}

new_posts = [p for p in posts if p["url"] not in existing_urls]

all_posts = existing + new_posts

with open("posts.json", "w") as f:
    json.dump(all_posts, f, indent=2)

print(f"Added {len(new_posts)} recent news signals")
