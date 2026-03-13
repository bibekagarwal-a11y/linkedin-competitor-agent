import html
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urljoin

import feedparser
import requests
from bs4 import BeautifulSoup

from common import (
    RAW_ITEMS_FILE,
    USER_AGENT,
    append_jsonl,
    classify_event_type,
    contains_any,
    ensure_dirs,
    item_id,
    keyword_score,
    load_competitors,
    normalize_text,
    parse_date,
    read_jsonl,
    safe_domain,
    utc_now_iso,
)

HEADERS = {"User-Agent": USER_AGENT}
TIMEOUT = 30


def fetch_url(url: str) -> Optional[str]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None


def extract_links(page_url: str, html_text: str, source_type: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html_text, "html.parser")
    results: List[Dict[str, str]] = []
    seen = set()

    for a in soup.find_all("a", href=True):
        title = normalize_text(a.get_text(" ", strip=True))
        href = urljoin(page_url, a["href"])

        if len(title) < 25:
            continue
        if href in seen:
            continue
        seen.add(href)

        results.append({
            "title": html.unescape(title),
            "url": href,
            "source_type": source_type,
        })

    return results[:40]


def google_news_rss(query: str) -> str:
    return (
        "https://news.google.com/rss/search?"
        f"q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    )


def collect_news(competitor: Dict[str, Any]) -> List[Dict[str, Any]]:
    query = competitor.get("news_query") or competitor["company"]
    feed_url = google_news_rss(query)
    parsed = feedparser.parse(feed_url)
    rows: List[Dict[str, Any]] = []

    for entry in parsed.entries[:20]:
        title = normalize_text(getattr(entry, "title", ""))
        url = getattr(entry, "link", "")
        published = parse_date(getattr(entry, "published", None))
        summary = normalize_text(BeautifulSoup(getattr(entry, "summary", ""), "html.parser").get_text(" ", strip=True))
        rows.append(
            build_item(
                competitor=competitor,
                source_type="news",
                title=title,
                url=url,
                published_at=published,
                snippet=summary,
                content=title + " " + summary,
            )
        )
    return [r for r in rows if r]


def collect_page_links(competitor: Dict[str, Any], field: str, source_type: str) -> List[Dict[str, Any]]:
    url = competitor.get(field)
    if not url:
        return []
    html_text = fetch_url(url)
    if not html_text:
        return []

    rows: List[Dict[str, Any]] = []
    for link in extract_links(url, html_text, source_type):
        rows.append(
            build_item(
                competitor=competitor,
                source_type=source_type,
                title=link["title"],
                url=link["url"],
                published_at=None,
                snippet=link["title"],
                content=link["title"],
            )
        )
    return [r for r in rows if r]


def collect_linkedin_feed(competitor: Dict[str, Any]) -> List[Dict[str, Any]]:
    feed_url = competitor.get("linkedin_feed_url")
    if not feed_url:
        return []

    parsed = feedparser.parse(feed_url)
    rows: List[Dict[str, Any]] = []

    for entry in parsed.entries[:20]:
        title = normalize_text(getattr(entry, "title", "")) or "LinkedIn post"
        url = getattr(entry, "link", competitor.get("linkedin_url", ""))
        published = parse_date(getattr(entry, "published", None))
        summary = normalize_text(BeautifulSoup(getattr(entry, "summary", ""), "html.parser").get_text(" ", strip=True))

        rows.append(
            build_item(
                competitor=competitor,
                source_type="linkedin",
                title=title,
                url=url,
                published_at=published,
                snippet=summary,
                content=f"{title} {summary}",
            )
        )

    return [r for r in rows if r]


def company_match_score(competitor: Dict[str, Any], text: str, url: str) -> int:
    text_l = (text or "").lower()
    score = 0

    names = [competitor.get("primary_name", ""), competitor.get("company", "")]
    names.extend(competitor.get("aliases", []))

    for name in names:
        if name and name.lower() in text_l:
            score += 3

    domain = competitor.get("domain", "").lower()
    if domain and domain in safe_domain(url):
        score += 5

    score += keyword_score(text, competitor)

    return score


def should_keep(competitor: Dict[str, Any], title: str, snippet: str, url: str) -> bool:
    text = f"{title} {snippet}".strip()

    if contains_any(text, competitor.get("exclude_terms", [])):
        return False

    score = company_match_score(competitor, text, url)
    return score >= 4


def build_item(
    competitor: Dict[str, Any],
    source_type: str,
    title: str,
    url: str,
    published_at: Optional[str],
    snippet: str,
    content: str,
) -> Optional[Dict[str, Any]]:
    title = normalize_text(title)
    snippet = normalize_text(snippet)
    content = normalize_text(content)

    if not title:
        return None

    if not should_keep(competitor, title, snippet, url):
        return None

    record = {
        "id": item_id(competitor["company"], source_type, url, title),
        "company": competitor["company"],
        "primary_name": competitor.get("primary_name", competitor["company"]),
        "source_type": source_type,
        "source_name": safe_domain(url) or source_type,
        "url": url,
        "title": title,
        "snippet": snippet,
        "content": content,
        "published_at": published_at,
        "fetched_at": utc_now_iso(),
        "event_type": classify_event_type(f"{title} {snippet} {content}"),
        "importance_score": company_match_score(competitor, f"{title} {snippet} {content}", url),
    }
    return record


def dedupe_new_rows(existing: List[Dict[str, Any]], new_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    existing_ids = {row["id"] for row in existing}
    unique_rows: List[Dict[str, Any]] = []

    for row in new_rows:
        if row["id"] not in existing_ids:
            existing_ids.add(row["id"])
            unique_rows.append(row)

    return unique_rows


def is_recent_enough(row: Dict[str, Any], days: int = 21) -> bool:
    published_at = row.get("published_at")
    if not published_at:
        return True

    try:
        dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return dt >= cutoff
    except Exception:
        return True


def main() -> None:
    ensure_dirs()
    competitors = load_competitors()
    existing = read_jsonl(RAW_ITEMS_FILE)

    all_rows: List[Dict[str, Any]] = []
    for competitor in competitors:
        rows: List[Dict[str, Any]] = []
        rows.extend(collect_news(competitor))
        rows.extend(collect_page_links(competitor, "blog_url", "blog"))
        rows.extend(collect_page_links(competitor, "press_url", "press"))
        rows.extend(collect_linkedin_feed(competitor))
        rows = [r for r in rows if is_recent_enough(r, days=30)]
        all_rows.extend(rows)

    new_rows = dedupe_new_rows(existing, all_rows)
    append_jsonl(RAW_ITEMS_FILE, new_rows)

    print(f"Collected {len(new_rows)} new normalized items.")


if __name__ == "__main__":
    main()
