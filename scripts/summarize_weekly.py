import json
import datetime
from collections import defaultdict

today = datetime.date.today()
week = today - datetime.timedelta(days=7)

with open("posts.json") as f:
    posts = json.load(f)

weekly_posts = [p for p in posts if p["date"] >= str(week)]

summary = f"# Weekly Competitor Summary ({today})\n\n"

grouped = defaultdict(list)

for p in weekly_posts:
    key = (p["company"], p["text"])
    grouped[key].append(p["url"])

if not grouped:
    summary += "No competitor activity detected.\n"

else:
    for (company, text), links in grouped.items():

        summary += f"**{company} — {text}**\n"

        for link in links:
            summary += f"- {link}\n"

        summary += "\n"


with open("weekly_summary.md", "w") as f:
    f.write(summary)
