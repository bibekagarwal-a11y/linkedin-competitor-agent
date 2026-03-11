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

# Read competitors list
with open("competitors.csv") as f:
    reader = csv.DictReader(f)

    for row in reader:

        company = row["company"]
        company_url = row["linkedin"]

        print(f"Checking LinkedIn page for {company}")

        try:
            response = requests.get(company_url, headers=headers)

            soup = BeautifulSoup(response.text, "html.parser")

            # Look for visible text snippets
            paragraphs = soup.find_all("span")

            for p in paragraphs:

                text = p.get_text(strip=True)

                if len(text) > 40:

                    post = {
                        "company": company,
                        "company_url": company_url,
                        "date": str(today),
                        "text": text
                    }

                    posts.append(post)

        except Exception as e:
            print(f"Error reading {company}: {e}")


# Load existing dataset
try:
    with open("posts.json") as f:
        existing_posts = json.load(f)

    if not isinstance(existing_posts, list):
        existing_posts = []

except:
    existing_posts = []

# Prevent duplicates
existing_texts = {p["text"] for p in existing_posts if "text" in p}

new_posts = [p for p in posts if p["text"] not in existing_texts]

all_posts = existing_posts + new_posts

# Save updated dataset
with open("posts.json", "w") as f:
    json.dump(all_posts, f, indent=2)

print(f"Added {len(new_posts)} new LinkedIn signals")
