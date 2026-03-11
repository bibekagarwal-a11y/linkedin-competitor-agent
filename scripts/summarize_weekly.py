import json
import datetime
from collections import defaultdict

today = datetime.date.today()
week_start = today - datetime.timedelta(days=7)

relevant_keywords = [
    "trading","forecast","forecasting","energy","power",
    "risk","algorithmic","intraday","day-ahead","battery",
    "renewable","portfolio","analytics","platform",
    "software","solution","launch","partnership","integration"
]

def relevant(text):
    text = text.lower()
    return any(k in text for k in relevant_keywords)

with open("posts.json") as f:
    posts = json.load(f)

weekly_posts = []

for p in posts:

    post_date = datetime.date.fromisoformat(p["date"])

    if week_start <= post_date <= today:

        if relevant(p["text"]):

            weekly_posts.append(p)

grouped = defaultdict(list)

for p in weekly_posts:
    grouped[p["company"]].append(p["text"])

summary = "# Competitor Intelligence – Last 7 Days\n\n"

if not grouped:
    summary += "No relevant competitor activity.\n"

else:

    for company, texts in grouped.items():

        summary += f"## {company}\n\n"

        unique_points = list(set(texts))

        for t in unique_points[:5]:
            summary += f"• {t}\n"

        summary += "\n"

with open("weekly_summary.md", "w") as f:
    f.write(summary)
