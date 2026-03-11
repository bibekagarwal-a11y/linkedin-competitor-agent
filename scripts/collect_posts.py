import json
import datetime

today = datetime.date.today()

posts = [
    {
        "company": "Volue",
        "date": str(today),
        "text": "Volue launches new energy forecasting platform",
        "url": "https://www.linkedin.com/company/volue/"
    },
    {
        "company": "GMSL",
        "date": str(today),
        "text": "GMSL announces partnership with energy market operator",
        "url": "https://www.linkedin.com/company/gmsl/"
    }
]

try:
    with open("posts.json") as f:
        existing = json.load(f)
except:
    existing = []

existing.extend(posts)

with open("posts.json", "w") as f:
    json.dump(existing, f, indent=2)

print("Test posts added")
