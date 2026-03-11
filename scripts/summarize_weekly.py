import json
import datetime
from collections import defaultdict

today = datetime.date.today()
week = today - datetime.timedelta(days=7)

# Load posts
with open("posts.json") as f:
    posts = json.load(f)

# Filter last 7 days
weekly_posts = [p for p in posts if p["date"] >= str(week)]

# Group by competitor
grouped = defaultdict(list)

for p in weekly_posts:
    grouped[p["company"]].append(p["text"])

summary = "# Competitor Intelligence – Last 7 Days\n\n"

if not grouped:
    summary += "No notable competitor activity.\n"

else:
    for company, texts in grouped.items():

        summary += f"## {company}\n\n"

        unique_points = list(set(texts))

        for t in unique_points[:5]:
            summary += f"• {t}\n"

        summary += "\n"

# Save report
with open("weekly_summary.md", "w") as f:
    f.write(summary)
