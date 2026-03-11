import requests
from bs4 import BeautifulSoup
import json
import datetime
import csv

today = datetime.date.today()

headers = {
    "User-Agent": "Mozilla/5.0"
}

posts = []

# Load competitors
with open("competitors.csv") as f:
    reader = csv.DictReader(f)

    for row in reader:

        company = row["company"]
        url = row["linkedin"]

        print(f"Checking posts for {company}")

        try:

            response = requests.get(url, headers=headers)

            soup = BeautifulSoup(response.text, "html.parser")

            links = soup.find_all("a")

            for link in links:

                href = link.get("href")

                if href and "linkedin.com/posts" in href:

                    post = post = {
    "company": company,
    "company_url": url,
    "date": str(today),
    "text": link.text.strip(),
    "url": href
}

                    if post["text"]:
                        posts.append(post)

        except Exception as e:

            print(f"Error reading {company}: {e}")

# Load existing posts
try:

    with open("posts.json") as f:
        existing = json.load(f)

except:

    existing = []

existing_urls = {p["url"] for p in existing if isinstance(p, dict) and "url" in p}

new_posts = [p for p in posts if p["url"] not in existing_urls]

all_posts = existing + new_posts

with open("posts.json", "w") as f:

    json.dump(all_posts, f, indent=2)

print(f"Added {len(new_posts)} new posts")
