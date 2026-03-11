import json
import datetime
from collections import defaultdict

today = datetime.date.today()
week_start = today - datetime.timedelta(days=7)

energy_keywords = [
    "trading","forecast","forecasting","energy","power",
    "intraday","day-ahead","portfolio","risk",
    "analytics","platform","software","integration",
    "renewable","battery","flexibility"
]

def relevant(text):
    text = text.lower()
    return any(k in text for k in energy_keywords)

with open("posts.json") as f:
    posts = json.load(f)

weekly = []

for p in posts:

    date = datetime.date.fromisoformat(p["date"])

    if week_start <= date <= today:
        if relevant(p["text"]):
            weekly.append(p)

grouped = defaultdict(list)

for p in weekly:
    grouped[p["company"]].append(p["text"])

report = "# Energy Trading Software – Competitor Intelligence\n"
report += f"Week of {today}\n\n"

if not grouped:
    report += "No relevant competitor developments detected.\n"

else:

    for company, texts in grouped.items():

        report += f"## {company}\n"

        unique = list(set(texts))

        for t in unique[:4]:
            report += f"• {t}\n"

        report += "\n"

with open("weekly_summary.md","w") as f:
    f.write(report)
