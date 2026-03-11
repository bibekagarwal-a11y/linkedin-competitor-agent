import json
import datetime

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

with open("posts.json") as f:
    posts = json.load(f)

daily_posts = [p for p in posts if p["date"] >= str(yesterday)]

summary = f"# Daily Competitor Activity ({today})\n\n"

if not daily_posts:
    summary += "No LinkedIn activity detected.\n"

else:
    for p in daily_posts:
        summary += f"{p['company']} — {p['text']}\n\n"

with open("daily_summary.md", "w") as f:
    f.write(summary)
