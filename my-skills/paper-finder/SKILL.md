---
name: paper-finder
description: |
  Academic paper search and discovery for PoC, research, and technical exploration.
  Searches Semantic Scholar, OpenAlex, and ArXiv APIs to find
  relevant papers with citation counts, abstracts, and download links.
  Supports keyword search, ArXiv ID lookup, DOI lookup, and BibTeX export.
  Use when user says "find papers", "paper search", "search papers",
  "find research", "academic search", "look up paper", "ArXiv search",
  or provides ArXiv IDs/DOIs to look up. Also triggers on /paper command.
  Outputs formatted markdown tables and optionally saves to docs/papers/.
license: MIT License
metadata:
  skill-author: jesamkim
  version: 1.0.0
---

# Paper Finder

## Overview

Search academic papers across multiple APIs and produce structured results with citation counts, abstracts, and links. Designed for PoC research, technical exploration, and literature review.

## Workflow

### 1. Keyword Search

Run the search script with user's keywords:

```bash
python3 {SKILL_DIR}/scripts/search_papers.py search "<keywords>" --limit 10
```

The script searches **Semantic Scholar** first. On rate limit (429) or failure, falls back to **OpenAlex**.

To search a specific source:

```bash
python3 {SKILL_DIR}/scripts/search_papers.py search "<keywords>" --source semantic
python3 {SKILL_DIR}/scripts/search_papers.py search "<keywords>" --source openalex
python3 {SKILL_DIR}/scripts/search_papers.py search "<keywords>" --source arxiv
```

### 2. Paper Lookup by ID

Look up a specific paper by ArXiv ID or DOI:

```bash
python3 {SKILL_DIR}/scripts/search_papers.py lookup --arxiv 2301.00234
python3 {SKILL_DIR}/scripts/search_papers.py lookup --doi 10.1145/1234567.1234568
```

### 3. Output Options

**Markdown table** (default): Displays results in terminal as a formatted table.

**Save to file**:

```bash
python3 {SKILL_DIR}/scripts/search_papers.py search "<keywords>" --output docs/papers/results.md
```

**BibTeX export**:

```bash
python3 {SKILL_DIR}/scripts/search_papers.py search "<keywords>" --bibtex docs/papers/results.bib
```

**Sort by citations**:

```bash
python3 {SKILL_DIR}/scripts/search_papers.py search "<keywords>" --sort citations
```

### 4. Present Results

After running the script, present results to the user as a markdown table:

| # | Title | Authors | Year | Citations | Link |
|---|-------|---------|------|-----------|------|

Include a brief summary of what was found and highlight the most relevant papers based on citation count and recency.

## Key Behaviors

- Always run the search script rather than constructing curl commands manually
- If the script is unavailable or fails, fall back to curl commands documented in `references/api_reference.md`
- Create `docs/papers/` directory before saving if it doesn't exist
- When user provides ArXiv IDs (e.g., 2301.00234), use the `lookup` command
- For broad research topics, suggest refining keywords if results are too generic
- Present results in Korean explanations with English paper titles preserved

## Rate Limit Notes

| API | Limit | Notes |
|-----|-------|-------|
| Semantic Scholar | 100 req/5min (no key) | Strict; get free key for higher limits |
| OpenAlex | ~100K req/day | Very generous; preferred fallback |
| ArXiv | 3 req/sec | Generous for normal use |

If Semantic Scholar returns 429, the script automatically retries with OpenAlex.
