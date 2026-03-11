import json
import datetime
import random

today = datetime.date.today()

example_posts = [
    "Launching a new energy trading platform",
    "Announcing partnership with power exchange",
    "Hiring engineers for algorithmic trading",
    "New forecasting tool for renewable markets"
]

post = {
    "company": "CompetitorA",
    "date": str(today),
    "text": random.choice(example_posts)
}

try:
    with open("posts.json") as f:
        data = json.load(f)
except:
    data = []

data.append(post)

with open("posts.json","w") as f:
    json.dump(data,f,indent=2)
