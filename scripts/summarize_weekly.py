import json
import datetime

today = datetime.date.today()
week = today - datetime.timedelta(days=7)

with open("posts.json") as f:
    posts = json.load(f)

weekly_posts = [p for p in posts if p["date"] >= str(week)]

summary = f"# Weekly Competitor Activity ({today})\n\n"

if not weekly_posts:
    summary += "No LinkedIn activity detected.\n"

else:
    for p in weekly_posts:
        summary += f"{p['company']} — {p['text']}\n\n"

with open("weekly_summary.md", "w") as f:
    f.write(summary)
