import json
import datetime
from collections import defaultdict
from transformers import pipeline

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

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

report = "# Competitor Intelligence – Last 7 Days\n\n"

for company, texts in grouped.items():

    combined = " ".join(texts[:10])

    try:
        summary = summarizer(combined, max_length=40, min_length=10)[0]["summary_text"]
    except:
        summary = texts[0]

    report += f"## {company}\n"
    report += f"• {summary}\n\n"

with open("weekly_summary.md","w") as f:
    f.write(report)
