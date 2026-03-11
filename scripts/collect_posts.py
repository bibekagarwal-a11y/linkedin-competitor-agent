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

# Read competitors
with open("competitors.csv") as f:
    reader = csv.DictReader(f)

    for row in reader:

        company = row["company"]
        company_url = row["linkedin"]

        print(f"Checking posts for {company}")

        try:

            response = requests.get(company_url, headers=headers)

            soup = BeautifulSoup(response.text, "html.parser")

            links = soup.find_all("a")

            for link in links:

                href = link.get("href")
                text = link.text.strip()

                # Capture real LinkedIn posts
                if href and "/posts/" in href:

                    post = {
                        "company": company,
                        "company_url": company_url,
                        "date": str(today),
                        "text": text if text else "LinkedIn post",
                        "url": href
                    }

                    posts.append(post)

        except Exception as e:

            print(f"Error reading {company}: {e}")


# Load existing posts
try:

    with open("posts.json") as f:
        existing_posts = json.load(f)

        if not isinstance(existing_posts, list):
            existing_posts = []

        existing_posts = [p for p in existing_posts if isinstance(p, dict)]

except:

    existing_posts = []


# Detect duplicates
existing_urls = {p["url"] for p in existing_posts if "url" in p}

new_posts = [p for p in posts if p["url"] not in existing_urls]

all_posts = existing_posts + new_posts


# Save updated dataset
with open("posts.json", "w") as f:
    json.dump(all_posts, f, indent=2)

print(f"Added {len(new_posts)} new posts")
