import json
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

today = datetime.date.today()
week = today - datetime.timedelta(days=7)

with open("posts.json") as f:
    posts = json.load(f)

weekly_posts = [p for p in posts if p["date"] >= str(week)]

summary = f"# Weekly Competitor Summary ({today})\n\n"

if not weekly_posts:
    summary += "No competitor activity detected.\n"

else:

    texts = [p["text"] for p in weekly_posts]

    vectorizer = TfidfVectorizer().fit_transform(texts)
    similarity_matrix = cosine_similarity(vectorizer)

    used = set()

    for i, post in enumerate(weekly_posts):

        if i in used:
            continue

        group = [i]

        for j in range(i + 1, len(weekly_posts)):

            if similarity_matrix[i][j] > 0.6:
                group.append(j)
                used.add(j)

        used.add(i)

        company = weekly_posts[i]["company"]
        headline = weekly_posts[i]["text"]

        summary += f"**{company} — {headline}**\n"

        for idx in group:
            link = weekly_posts[idx]["url"]
            summary += f"- {link}\n"

        summary += "\n"


with open("weekly_summary.md", "w") as f:
    f.write(summary)
