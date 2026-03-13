# Competitor Intelligence Agent

This repository builds a **deduplicated weekly competitor-intelligence digest**.

It collects:
- general news coverage
- competitor blog posts
- press / newsroom links
- optional LinkedIn feed items if you provide a feed URL

Then it:
1. normalizes source items
2. filters by company-aware relevance
3. clusters duplicate coverage into one canonical event
4. generates a weekly markdown report

## Why this repo is structured this way

The goal is not to dump raw headlines.

The goal is to answer:

- What happened this week?
- Why does it matter?
- Which competitor is moving?
- Is this really a new event, or just the same story repeated across outlets?

## Repository layout

```text
competitors.csv
requirements.txt
scripts/
  common.py
  collect_sources.py
  cluster_events.py
  generate_weekly_report.py
data/
  raw_items.jsonl
  canonical_events.json
reports/
  weekly_report.md
.github/workflows/
  collect.yml
  report.yml
