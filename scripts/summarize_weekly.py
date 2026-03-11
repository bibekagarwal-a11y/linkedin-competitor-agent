import json
import datetime

today = datetime.date.today()
week = today - datetime.timedelta(days=7)

# Load posts
with open("posts.json") as f:
    posts = json.load(f)

# Filter last 7 days
weekly_posts = [p for p in posts if p["date"] >= str(week)]

summary = f"# Weekly Competitor Summary ({today})\n\n"

if not weekly_posts:
    summary += "No competitor activity detected in the last 7 days.\n"

else:
    for p in weekly_posts:
        summary += f"- [{p['company']}]({p.get('company_url','')}) — {p['text']}  \n"
        summary += f"  👉 [View Post]({p['url']})\n\n"

# Save report
with open("weekly_summary.md", "w") as f:
    f.write(summary)
