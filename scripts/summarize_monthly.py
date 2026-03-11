import json
import datetime

today = datetime.date.today()
month = today - datetime.timedelta(days=30)

# Load posts
with open("posts.json") as f:
    posts = json.load(f)

# Filter last 30 days
monthly_posts = [p for p in posts if p["date"] >= str(month)]

summary = f"# Monthly Competitor Summary ({today})\n\n"

if not monthly_posts:
    summary += "No competitor activity detected in the last 30 days.\n"
else:
    for p in monthly_posts:
        summary += f"- **{p['company']}** — {p['text']}  \n"
        summary += f"  🔗 {p['url']}\n\n"

# Save report
with open("monthly_summary.md", "w") as f:
    f.write(summary)
