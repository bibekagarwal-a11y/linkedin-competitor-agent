from collections import defaultdict
from difflib import SequenceMatcher
from typing import Any, Dict, List

from common import (
    EVENTS_FILE,
    RAW_ITEMS_FILE,
    ensure_dirs,
    normalized_title,
    read_jsonl,
    source_rank,
    stable_hash,
    write_json,
)


def similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def same_event(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    if a["company"] != b["company"]:
        return False

    ta = normalized_title(a.get("title", ""))
    tb = normalized_title(b.get("title", ""))

    if ta == tb:
        return True

    if similarity(ta, tb) >= 0.84:
        return True

    tokens_a = set(ta.split())
    tokens_b = set(tb.split())
    overlap = len(tokens_a & tokens_b)
    union = max(len(tokens_a | tokens_b), 1)
    jaccard = overlap / union

    if a.get("event_type") == b.get("event_type") and jaccard >= 0.45:
        return True

    return False


def cluster_company_items(items: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    clusters: List[List[Dict[str, Any]]] = []

    for item in sorted(items, key=lambda x: (x.get("published_at") or "", -x.get("importance_score", 0))):
        placed = False
        for cluster in clusters:
            if same_event(item, cluster[0]):
                cluster.append(item)
                placed = True
                break
        if not placed:
            clusters.append([item])

    return clusters


def choose_primary_item(cluster: List[Dict[str, Any]]) -> Dict[str, Any]:
    return sorted(
        cluster,
        key=lambda x: (
            -x.get("importance_score", 0),
            -source_rank(x.get("source_type", ""), x.get("source_name", "")),
            x.get("published_at") or "",
        ),
    )[0]


def summarize_cluster(cluster: List[Dict[str, Any]]) -> Dict[str, Any]:
    primary = choose_primary_item(cluster)
    titles = [x["title"] for x in cluster]

    merged_sources = []
    seen = set()
    for item in cluster:
        label = f'{item["source_type"]}:{item["source_name"]}'
        if label not in seen:
            seen.add(label)
            merged_sources.append(label)

    return {
        "event_id": stable_hash({"company": primary["company"], "title": normalized_title(primary["title"])})[:20],
        "company": primary["company"],
        "event_type": primary.get("event_type", "general_update"),
        "headline": primary["title"],
        "canonical_url": primary["url"],
        "published_at": primary.get("published_at"),
        "importance_score": max(x.get("importance_score", 0) for x in cluster),
        "coverage_count": len(cluster),
        "sources": merged_sources,
        "supporting_items": [
            {
                "title": item["title"],
                "url": item["url"],
                "source_type": item["source_type"],
                "source_name": item["source_name"],
                "published_at": item.get("published_at"),
            }
            for item in sorted(cluster, key=lambda x: (x.get("published_at") or "", x["title"]))
        ],
        "summary_basis": titles[:5],
    }


def why_it_matters(event_type: str, headline: str) -> str:
    text = headline.lower()

    if event_type == "funding_mna":
        return "This can signal fresh capital, ownership change, or a strategic push that may affect product investment and market positioning."
    if event_type == "partnership":
        return "This may expand distribution, data access, or implementation reach, which can strengthen go-to-market execution."
    if event_type == "product_launch":
        return "This suggests roadmap movement and may indicate where the competitor is trying to differentiate."
    if event_type == "leadership":
        return "Leadership changes often precede strategy shifts, reorganizations, or a new commercial emphasis."
    if event_type == "customer_win":
        return "This may validate product-market fit and create proof points for future sales."
    if event_type == "expansion":
        return "This points to geographic or segment expansion and may indicate where competitive pressure will increase."
    if event_type == "thought_leadership":
        return "Repeated messaging here can reveal positioning, category creation efforts, or demand-gen themes."
    if "battery" in text or "trading" in text or "forecast" in text:
        return "This appears directly relevant to the product and market themes you are tracking."
    return "This appears notable enough to track and may matter if repeated across multiple weeks or sources."


def main() -> None:
    ensure_dirs()
    items = read_jsonl(RAW_ITEMS_FILE)

    by_company: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for item in items:
        by_company[item["company"]].append(item)

    events: List[Dict[str, Any]] = []
    for _, company_items in by_company.items():
        clusters = cluster_company_items(company_items)
        for cluster in clusters:
            event = summarize_cluster(cluster)
            event["why_it_matters"] = why_it_matters(event["event_type"], event["headline"])
            events.append(event)

    events = sorted(
        events,
        key=lambda x: (
            -x.get("importance_score", 0),
            -x.get("coverage_count", 0),
            x.get("published_at") or "",
        ),
        reverse=False,
    )

    write_json(EVENTS_FILE, events)
    print(f"Wrote {len(events)} canonical events.")


if __name__ == "__main__":
    main()
