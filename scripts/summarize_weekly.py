import json
import datetime

today = datetime.date.today()
week = today - datetime.timedelta(days=7)

with open("posts.json") as f:
    posts = json.load(f)

weekly_posts = [p for p in posts if p["date"] >= str(week)]

summary = f"# Weekly Competitor Summary ({today})\n\n"

for p in weekly_posts:
summary += f"- [{p['company']}](https://www.linkedin.com/company/{p['company'].lower()}/) — {p['text']}  \n"
summary += f"  👉 [View LinkedIn Post]({p['url']})\n\n"

with open("weekly_summary.md","w") as f:
    f.write(summary)
