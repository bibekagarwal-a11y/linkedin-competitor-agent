from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from common import (
    EVENTS_FILE,
    WEEKLY_REPORT_FILE,
    ensure_dirs,
    format_date_short,
    read_json,
)


def in_last_days(iso_date: str, days: int = 7) -> bool:
    if not iso_date:
        return False
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return dt >= cutoff
    except Exception:
        return False


def event_sort_key(event: Dict[str, Any]):
    return (
        event.get("importance_score", 0),
        event.get("coverage_count", 0),
        event.get("published_at") or "",
    )


def render_event(event: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"### {event['headline']}")
    lines.append("")
    lines.append(f"- **Type:** {event['event_type']}")
    lines.append(f"- **Date:** {format_date_short(event.get('published_at'))}")
    lines.append(f"- **Coverage:** {event.get('coverage_count', 0)} source(s)")
    lines.append(f"- **Why it matters:** {event['why_it_matters']}")
    lines.append(f"- **Primary link:** {event['canonical_url']}")
    if event.get("supporting_items"):
        lines.append("- **Supporting coverage:**")
        for item in event["supporting_items"][:5]:
            lines.append(f"  - {item['title']} ({item['source_type']}, {item['source_name']})")
    lines.append("")
    return "\n".join(lines)


def find_repeated_themes(events: List[Dict[str, Any]]) -> List[str]:
    counts = defaultdict(int)

    mapping = {
        "funding_mna": "Funding / ownership activity",
        "partnership": "Partnership momentum",
        "product_launch": "Product roadmap movement",
        "leadership": "Leadership changes",
        "customer_win": "Customer traction",
        "expansion": "Market expansion",
        "thought_leadership": "Thought-leadership positioning",
        "general_update": "General update flow",
    }

    for event in events:
        counts[event.get("event_type", "general_update")] += 1

    themes = []
    for key, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        if count >= 2:
            themes.append(f"{mapping.get(key, key)} appeared {count} times.")
    return themes


def main() -> None:
    ensure_dirs()
    events = read_json(EVENTS_FILE, [])

    weekly_events = [e for e in events if in_last_days(e.get("published_at"), 7)]
    weekly_events.sort(key=event_sort_key, reverse=True)

    by_company: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for event in weekly_events:
        by_company[event["company"]].append(event)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines: List[str] = []
    lines.append("# Weekly Competitor Intelligence")
    lines.append("")
    lines.append(f"Week ending {today}")
    lines.append("")

    if not weekly_events:
        lines.append("No high-signal competitor events were found in the last 7 days.")
        lines.append("")
    else:
        lines.append("## Top signals this week")
        lines.append("")
        for event in weekly_events[:10]:
            lines.append(
                f"- **{event['company']}** — {event['headline']} "
                f"({event['coverage_count']} source(s), {event['event_type']})"
            )
        lines.append("")

        for company, company_events in sorted(by_company.items()):
            lines.append(f"## {company}")
            lines.append("")

            for event in company_events[:5]:
                lines.append(render_event(event))

            repeated_themes = find_repeated_themes(company_events)
            if repeated_themes:
                lines.append("### Repeated themes")
                lines.append("")
                for theme in repeated_themes:
                    lines.append(f"- {theme}")
                lines.append("")

    lines.append("## Method notes")
    lines.append("")
    lines.append("- Same-story coverage from multiple channels is clustered into one canonical event.")
    lines.append("- Company matching uses aliases, domains, include terms, and exclude terms.")
    lines.append("- Lower-confidence or generic mentions should be reviewed before acting on them.")
    lines.append("")

    with open(WEEKLY_REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote {WEEKLY_REPORT_FILE}")


if __name__ == "__main__":
    main()
