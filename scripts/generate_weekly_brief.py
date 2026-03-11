import json
import datetime
from collections import defaultdict

today = datetime.date.today()
week_start = today - datetime.timedelta(days=7)

energy_keywords = [
    "trading",
    "forecast",
    "forecasting",
    "power",
    "energy",
    "intraday",
    "day-ahead",
    "portfolio",
    "risk",
    "analytics",
    "platform",
    "software",
    "integration",
    "renewable",
    "battery",
    "flexibility"
]

def relevant(text):
    text = text.lower()
    return any(k in text for k in energy_keywords)

try:
    with open("signals.json") as f:
        signals = json.load(f)
except:
    signals = []

weekly_signals = []

for s in signals:

    try:
        date = datetime.date.fromisoformat(s["date"])
    except:
        continue

    if week_start <= date <= today:

        if relevant(s["text"]):

            weekly_signals.append(s)

grouped = defaultdict(list)

for s in weekly_signals:
    grouped[s["company"]].append(s["text"])

report = "# Competitor Intelligence\n"
report += f"Week of {today}\n\n"

if not grouped:
    report += "No relevant competitor activity detected.\n"

else:

    for company, texts in grouped.items():

        report += f"## {company}\n\n"

        unique = []

        for t in texts:

            short = t.strip()

            if short not in unique and len(short) > 40:

                unique.append(short)

        for t in unique[:5]:

            report += f"• {t}\n"

        report += "\n"

with open("weekly_summary.md","w") as f:
    f.write(report)
