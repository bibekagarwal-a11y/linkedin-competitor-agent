import json
import datetime

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

with open("posts.json") as f:
    posts = json.load(f)

daily_posts = [p for p in posts if p["date"] >= str(yesterday)]

summary = f"# Daily Competitor Summary ({today})\n\n"

for p in daily_posts:
summary += f"- [{p['company']}](https://www.linkedin.com/company/{p['company'].lower()}/) — {p['text']}  \n"
summary += f"  👉 [View LinkedIn Post]({p['url']})\n\n"

with open("daily_summary.md","w") as f:
    f.write(summary)
