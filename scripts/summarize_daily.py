import json
import datetime

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

# Load posts
with open("posts.json") as f:
    posts = json.load(f)

# Filter last 24h
daily_posts = [p for p in posts if p["date"] >= str(yesterday)]

summary = f"# Daily Competitor Summary ({today})\n\n"

if not daily_posts:
    summary += "No competitor activity detected in the last 24 hours.\n"

else:
    for p in daily_posts:
        summary += f"- [{p['company']}]({p.get('company_url','')}) — {p['text']}  \n"
        summary += f"  👉 [View Post]({p['url']})\n\n"

# Save report
with open("daily_summary.md", "w") as f:
    f.write(summary)
