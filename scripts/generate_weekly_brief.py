import json
import datetime
from collections import defaultdict

today = datetime.date.today()
week_start = today - datetime.timedelta(days=7)

energy_keywords = [
    "trading","forecast","forecasting","power","energy",
    "intraday","day-ahead","portfolio","risk",
    "analytics","platform","software","integration",
    "renewable","battery","flexibility"
]

def relevant(text):
    text = text.lower()
    return any(k in text for k in energy_keywords)

try:
    with open("signals.json") as f:
        signals = json.load(f)
except:
    signals = []

weekly = []

for s in signals:

    try:
        date = datetime.date.fromisoformat(s["date"])
    except:
        continue

    if week_start <= date <= today:
        if relevant(s["text"]):
            weekly.append(s)

grouped = defaultdict(list)

for s in weekly:
    grouped[s["company"]].append(s["text"])

report = "# Energy Trading Software – Competitor Intelligence\n"
report += f"Week of {today}\n\n"

if not grouped:
    report += "No relevant competitor activity detected.\n"

else:

    for company, texts in grouped.items():

        report += f"## {company}\n"

        unique = list(set(texts))

        for t in unique[:4]:
            report += f"• {t}\n"

        report += "\n"

with open("weekly_summary.md","w") as f:
    f.write(report)
