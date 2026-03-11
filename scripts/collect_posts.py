import feedparser
import json
import datetime
import csv

today = datetime.date.today()

posts = []

with open("competitors.csv") as f:
    reader = csv.DictReader(f)

    for row in reader:

        company = row["company"]
        company_url = row["linkedin"]

        print(f"Checking posts for {company}")

        # Extract company slug
        slug = company_url.rstrip("/").split("/")[-1]

        # RSSHub LinkedIn company feed
        feed_url = f"https://rsshub.app/linkedin/company/{slug}"

        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:

post = {
    "company": company,
    "company_url": company_url,
    "date": str(today),
    "text": text
}

            posts.append(post)


# Load existing posts
try:

    with open("posts.json") as f:
        existing_posts = json.load(f)

        if not isinstance(existing_posts, list):
            existing_posts = []

except:

    existing_posts = []


existing_urls = {p["url"] for p in existing_posts if "url" in p}

new_posts = [p for p in posts if p["url"] not in existing_urls]

all_posts = existing_posts + new_posts


with open("posts.json", "w") as f:
    json.dump(all_posts, f, indent=2)

print(f"Added {len(new_posts)} new posts")
