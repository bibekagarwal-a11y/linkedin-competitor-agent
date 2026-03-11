import json
import datetime

today = datetime.date.today()

with open("posts.json") as f:
    posts = json.load(f)

signals = {
    "product": [],
    "partnership": [],
    "hiring": [],
    "other": []
}

for p in posts:

    text = p["text"].lower()

    if "launch" in text or "platform" in text or "solution" in text:
        signals["product"].append(p)

    elif "partner" in text or "collaboration" in text:
        signals["partnership"].append(p)

    elif "hiring" in text or "join our team" in text or "career" in text:
        signals["hiring"].append(p)

    else:
        signals["other"].append(p)

report = f"# Competitor Intelligence ({today})\n\n"

report += "## Product Signals\n"
for s in signals["product"]:
    report += f"- {s['company']}: {s['text']}\n"

report += "\n## Partnership Signals\n"
for s in signals["partnership"]:
    report += f"- {s['company']}: {s['text']}\n"

report += "\n## Hiring Signals\n"
for s in signals["hiring"]:
    report += f"- {s['company']}: {s['text']}\n"

report += "\n## Other Activity\n"
for s in signals["other"]:
    report += f"- {s['company']}: {s['text']}\n"

with open("competitor_intelligence.md","w") as f:
    f.write(report)
