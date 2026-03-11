import json
import datetime

today = datetime.date.today()
month = today - datetime.timedelta(days=30)

with open("posts.json") as f:
    posts = json.load(f)

monthly_posts = [p for p in posts if p["date"] >= str(month)]

summary = f"# Monthly Competitor Summary ({today})\n\n"
summary += f"Posts from last 30 days\n\n"

for p in monthly_posts:
    summary += f"- {p['company']}: {p['text']}\n"

with open("monthly_summary.md","w") as f:
    f.write(summary)
