import csv
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from dateutil import parser as date_parser

DATA_DIR = Path("data")
REPORTS_DIR = Path("reports")
RAW_ITEMS_FILE = DATA_DIR / "raw_items.jsonl"
EVENTS_FILE = DATA_DIR / "canonical_events.json"
WEEKLY_REPORT_FILE = REPORTS_DIR / "weekly_report.md"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


def ensure_dirs() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_competitors(path: str = "competitors.csv") -> List[Dict[str, Any]]:
    competitors: List[Dict[str, Any]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["aliases"] = split_pipe(row.get("aliases", ""))
            row["include_terms"] = split_pipe(row.get("include_terms", ""))
            row["exclude_terms"] = split_pipe(row.get("exclude_terms", ""))
            row["priority"] = int(row.get("priority") or 0)
            competitors.append(row)
    return competitors


def split_pipe(value: str) -> List[str]:
    if not value:
        return []
    return [x.strip() for x in value.split("|") if x.strip()]


def normalize_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"\s+", " ", text).strip()
    return text


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def normalized_title(text: str) -> str:
    text = normalize_text(text).lower()
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\b(the|a|an|and|or|for|with|from|to|of|in|on|at|by)\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        dt = date_parser.parse(value)
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()
    except Exception:
        return None


def safe_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def stable_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def item_id(company: str, source_type: str, url: str, title: str) -> str:
    payload = {
        "company": company,
        "source_type": source_type,
        "url": url or "",
        "title": normalized_title(title),
    }
    return stable_hash(payload)[:24]


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    with open(path, "a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, payload: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def contains_any(text: str, terms: List[str]) -> bool:
    text_l = (text or "").lower()
    return any(term.lower() in text_l for term in terms)


def keyword_score(text: str, competitor: Dict[str, Any]) -> int:
    score = 0
    text_l = (text or "").lower()

    for term in competitor.get("include_terms", []):
        if term.lower() in text_l:
            score += 2

    important_signals = [
        "launch", "launched", "partnership", "partnered", "acquisition",
        "acquires", "acquired", "investment", "investor", "funding",
        "expands", "expansion", "customer", "contract", "hiring",
        "appointed", "appoints", "ceo", "cto", "battery", "trading",
        "forecasting", "intraday", "day-ahead", "platform", "software",
        "integration", "renewable", "gas", "power", "energy"
    ]
    for term in important_signals:
        if term in text_l:
            score += 1

    return score


def classify_event_type(text: str) -> str:
    text_l = (text or "").lower()
    rules = [
        ("funding_mna", ["investment", "investor", "funding", "acquire", "acquired", "acquisition", "backing"]),
        ("partnership", ["partnership", "partnered", "alliance", "collaboration"]),
        ("product_launch", ["launch", "launched", "release", "released", "introduces", "unveils"]),
        ("leadership", ["ceo", "cto", "cfo", "appointed", "joins as", "named as"]),
        ("customer_win", ["customer", "contract", "selected by", "chosen by"]),
        ("expansion", ["expand", "expansion", "new market", "opened", "opening"]),
        ("thought_leadership", ["webinar", "report", "insight", "opinion", "trend", "outlook"]),
    ]
    for label, keywords in rules:
        if any(k in text_l for k in keywords):
            return label
    return "general_update"


def source_rank(source_type: str, domain: str) -> int:
    score = 0
    if source_type == "press":
        score += 4
    elif source_type == "blog":
        score += 3
    elif source_type == "linkedin":
        score += 2
    elif source_type == "news":
        score += 1

    if domain:
        score += 1
    return score


def format_date_short(iso_value: Optional[str]) -> str:
    if not iso_value:
        return "unknown date"
    try:
        dt = date_parser.parse(iso_value)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return iso_value or "unknown date"
