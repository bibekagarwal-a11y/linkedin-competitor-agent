import feedparser
import pandas as pd
import json
import datetime

competitors = {
    "Volue": "https://www.linkedin.com/company/volue/posts/",
    "GMSL": "https://www.linkedin.com/company/gmsl/posts/"
}

today = datetime.date.today()

posts = []

for company, url in competitors.items():

    feed = feedparser.parse(url)

    for entry in feed.entries[:5]:

        post = {
            "company": company,
            "date": str(today),
            "text": entry.title
        }

        posts.append(post)

try:
    with open("posts.json") as f:
        existing = json.load(f)
except:
    existing = []

existing.extend(posts)

with open("posts.json","w") as f:
    json.dump(existing,f,indent=2)
