#!/usr/bin/env python3
"""Academic paper search across multiple APIs.

Supports Semantic Scholar, OpenAlex, and ArXiv.
Outputs formatted markdown tables with optional BibTeX export.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Paper:
    title: str = ""
    authors: list = field(default_factory=list)
    year: int = 0
    citations: int = 0
    url: str = ""
    abstract: str = ""
    arxiv_id: str = ""
    doi: str = ""
    source: str = ""


def fetch_json(url: str, retries: int = 2, delay: float = 2.0) -> dict | None:
    """Fetch JSON from URL with retry logic."""
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "PaperFinder/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                wait = delay * (attempt + 1)
                print(f"[Rate limited] Waiting {wait}s before retry...", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"[HTTP {e.code}] {url}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"[Error] {e}", file=sys.stderr)
            return None
    return None


def fetch_xml(url: str) -> ET.Element | None:
    """Fetch and parse XML from URL."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PaperFinder/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return ET.fromstring(resp.read())
    except Exception as e:
        print(f"[Error] {e}", file=sys.stderr)
        return None


# --- Search Functions ---


def search_semantic_scholar(query: str, limit: int = 10) -> list[Paper]:
    """Search Semantic Scholar API."""
    encoded = urllib.parse.quote(query)
    url = (
        f"https://api.semanticscholar.org/graph/v1/paper/search"
        f"?query={encoded}&limit={limit}"
        f"&fields=title,authors,year,citationCount,url,externalIds,abstract"
    )
    data = fetch_json(url)
    if not data or "data" not in data:
        return []

    papers = []
    for item in data["data"]:
        ext_ids = item.get("externalIds") or {}
        authors_list = [a.get("name", "") for a in (item.get("authors") or [])]
        papers.append(Paper(
            title=item.get("title", ""),
            authors=authors_list,
            year=item.get("year") or 0,
            citations=item.get("citationCount") or 0,
            url=item.get("url", ""),
            abstract=item.get("abstract") or "",
            arxiv_id=ext_ids.get("ArXiv", ""),
            doi=ext_ids.get("DOI", ""),
            source="semantic_scholar",
        ))
    return papers


def search_openalex(query: str, limit: int = 10) -> list[Paper]:
    """Search OpenAlex API."""
    encoded = urllib.parse.quote(query)
    url = (
        f"https://api.openalex.org/works"
        f"?search={encoded}&per_page={limit}"
        f"&select=title,authorships,publication_year,cited_by_count,doi,id"
    )
    data = fetch_json(url)
    if not data or "results" not in data:
        return []

    papers = []
    for item in data["results"]:
        authors_list = []
        for authorship in (item.get("authorships") or []):
            author = authorship.get("author", {})
            name = author.get("display_name", "")
            if name:
                authors_list.append(name)

        doi_raw = item.get("doi") or ""
        doi_val = doi_raw.replace("https://doi.org/", "") if doi_raw else ""

        papers.append(Paper(
            title=item.get("title") or "",
            authors=authors_list,
            year=item.get("publication_year") or 0,
            citations=item.get("cited_by_count") or 0,
            url=doi_raw or item.get("id", ""),
            doi=doi_val,
            source="openalex",
        ))
    return papers


def search_arxiv(query: str, limit: int = 10) -> list[Paper]:
    """Search ArXiv API."""
    encoded = urllib.parse.quote(query)
    url = (
        f"http://export.arxiv.org/api/query"
        f"?search_query=all:{encoded}&start=0&max_results={limit}"
        f"&sortBy=relevance&sortOrder=descending"
    )
    root = fetch_xml(url)
    if root is None:
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    papers = []
    for entry in root.findall("atom:entry", ns):
        title = (entry.findtext("atom:title", "", ns) or "").strip().replace("\n", " ")
        authors_list = [
            a.findtext("atom:name", "", ns)
            for a in entry.findall("atom:author", ns)
        ]
        published = entry.findtext("atom:published", "", ns)
        year = int(published[:4]) if published and len(published) >= 4 else 0

        # Extract ArXiv ID from entry id URL
        entry_id = entry.findtext("atom:id", "", ns)
        arxiv_id = entry_id.split("/abs/")[-1] if "/abs/" in entry_id else ""
        # Remove version suffix for clean ID
        arxiv_id_clean = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id

        abstract = (entry.findtext("atom:summary", "", ns) or "").strip().replace("\n", " ")

        # Get PDF link
        pdf_link = ""
        for link in entry.findall("atom:link", ns):
            if link.get("title") == "pdf":
                pdf_link = link.get("href", "")
                break

        papers.append(Paper(
            title=title,
            authors=authors_list,
            year=year,
            citations=0,  # ArXiv doesn't provide citation counts
            url=pdf_link or entry_id,
            abstract=abstract,
            arxiv_id=arxiv_id_clean,
            source="arxiv",
        ))
    return papers


# --- Lookup Functions ---


def lookup_arxiv_id(arxiv_id: str) -> Paper | None:
    """Look up a specific paper by ArXiv ID via Semantic Scholar."""
    url = (
        f"https://api.semanticscholar.org/graph/v1/paper/ArXiv:{arxiv_id}"
        f"?fields=title,authors,year,citationCount,url,externalIds,abstract"
    )
    data = fetch_json(url)
    if not data:
        return None

    ext_ids = data.get("externalIds") or {}
    authors_list = [a.get("name", "") for a in (data.get("authors") or [])]
    return Paper(
        title=data.get("title", ""),
        authors=authors_list,
        year=data.get("year") or 0,
        citations=data.get("citationCount") or 0,
        url=data.get("url", ""),
        abstract=data.get("abstract") or "",
        arxiv_id=ext_ids.get("ArXiv", arxiv_id),
        doi=ext_ids.get("DOI", ""),
        source="semantic_scholar",
    )


def lookup_doi(doi: str) -> Paper | None:
    """Look up a specific paper by DOI via Semantic Scholar."""
    url = (
        f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"
        f"?fields=title,authors,year,citationCount,url,externalIds,abstract"
    )
    data = fetch_json(url)
    if not data:
        return None

    ext_ids = data.get("externalIds") or {}
    authors_list = [a.get("name", "") for a in (data.get("authors") or [])]
    return Paper(
        title=data.get("title", ""),
        authors=authors_list,
        year=data.get("year") or 0,
        citations=data.get("citationCount") or 0,
        url=data.get("url", ""),
        abstract=data.get("abstract") or "",
        arxiv_id=ext_ids.get("ArXiv", ""),
        doi=ext_ids.get("DOI", doi),
        source="semantic_scholar",
    )


# --- Output Formatting ---


def format_authors(authors: list, max_authors: int = 3) -> str:
    """Format author list, truncating if needed."""
    if not authors:
        return "Unknown"
    if len(authors) <= max_authors:
        return ", ".join(authors)
    return ", ".join(authors[:max_authors]) + f" et al. (+{len(authors) - max_authors})"


def to_markdown_table(papers: list[Paper]) -> str:
    """Format papers as a markdown table."""
    if not papers:
        return "No papers found."

    lines = [
        "| # | Title | Authors | Year | Citations | Link |",
        "|---|-------|---------|------|-----------|------|",
    ]
    for i, p in enumerate(papers, 1):
        title = p.title[:80] + "..." if len(p.title) > 80 else p.title
        authors = format_authors(p.authors)
        cite_str = str(p.citations) if p.citations > 0 else "-"
        link = f"[Link]({p.url})" if p.url else "-"
        lines.append(f"| {i} | {title} | {authors} | {p.year or '-'} | {cite_str} | {link} |")

    return "\n".join(lines)


def to_markdown_detail(papers: list[Paper]) -> str:
    """Format papers as detailed markdown with abstracts."""
    if not papers:
        return "No papers found."

    sections = []
    for i, p in enumerate(papers, 1):
        authors = format_authors(p.authors, max_authors=5)
        cite_str = str(p.citations) if p.citations > 0 else "N/A"
        ids = []
        if p.arxiv_id:
            ids.append(f"ArXiv: {p.arxiv_id}")
        if p.doi:
            ids.append(f"DOI: {p.doi}")
        id_str = " | ".join(ids) if ids else ""

        section = f"### {i}. {p.title}\n\n"
        section += f"- **Authors**: {authors}\n"
        section += f"- **Year**: {p.year or 'N/A'}\n"
        section += f"- **Citations**: {cite_str}\n"
        if id_str:
            section += f"- **IDs**: {id_str}\n"
        if p.url:
            section += f"- **URL**: {p.url}\n"
        if p.abstract:
            abstract = p.abstract[:300] + "..." if len(p.abstract) > 300 else p.abstract
            section += f"\n> {abstract}\n"
        sections.append(section)

    return "\n".join(sections)


def to_bibtex(papers: list[Paper]) -> str:
    """Format papers as BibTeX entries."""
    entries = []
    for i, p in enumerate(papers, 1):
        first_author = p.authors[0].split()[-1].lower() if p.authors else "unknown"
        key = f"{first_author}{p.year or 'nd'}_{i}"
        author_str = " and ".join(p.authors) if p.authors else "Unknown"

        entry = f"@article{{{key},\n"
        entry += f"  title = {{{p.title}}},\n"
        entry += f"  author = {{{author_str}}},\n"
        if p.year:
            entry += f"  year = {{{p.year}}},\n"
        if p.doi:
            entry += f"  doi = {{{p.doi}}},\n"
        if p.arxiv_id:
            entry += f"  eprint = {{{p.arxiv_id}}},\n"
            entry += f"  archivePrefix = {{arXiv}},\n"
        if p.url:
            entry += f"  url = {{{p.url}}},\n"
        entry += "}"
        entries.append(entry)

    return "\n\n".join(entries)


# --- Main ---


SEARCH_FUNCTIONS = {
    "semantic": search_semantic_scholar,
    "openalex": search_openalex,
    "arxiv": search_arxiv,
}


def do_search(query: str, source: str = "auto", limit: int = 10, sort: str = "relevance") -> list[Paper]:
    """Search papers with automatic fallback."""
    papers = []

    if source == "auto":
        # Try Semantic Scholar first, fallback to OpenAlex
        papers = search_semantic_scholar(query, limit)
        if not papers:
            print("[Info] Semantic Scholar returned no results, trying OpenAlex...", file=sys.stderr)
            papers = search_openalex(query, limit)
    elif source in SEARCH_FUNCTIONS:
        papers = SEARCH_FUNCTIONS[source](query, limit)
    else:
        print(f"[Error] Unknown source: {source}. Use: semantic, openalex, arxiv", file=sys.stderr)
        return []

    if sort == "citations":
        papers = sorted(papers, key=lambda p: p.citations, reverse=True)
    elif sort == "year":
        papers = sorted(papers, key=lambda p: p.year, reverse=True)

    return papers


def main():
    parser = argparse.ArgumentParser(description="Academic paper search tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for papers by keywords")
    search_parser.add_argument("query", help="Search keywords")
    search_parser.add_argument("--source", default="auto", choices=["auto", "semantic", "openalex", "arxiv"])
    search_parser.add_argument("--limit", type=int, default=10)
    search_parser.add_argument("--sort", default="relevance", choices=["relevance", "citations", "year"])
    search_parser.add_argument("--output", help="Save markdown results to file")
    search_parser.add_argument("--bibtex", help="Save BibTeX to file")
    search_parser.add_argument("--detail", action="store_true", help="Show detailed output with abstracts")

    # Lookup command
    lookup_parser = subparsers.add_parser("lookup", help="Look up a specific paper")
    lookup_parser.add_argument("--arxiv", help="ArXiv ID (e.g., 2301.00234)")
    lookup_parser.add_argument("--doi", help="DOI (e.g., 10.1145/1234567)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "search":
        papers = do_search(args.query, args.source, args.limit, args.sort)

        if args.detail:
            result = to_markdown_detail(papers)
        else:
            result = to_markdown_table(papers)
        print(result)

        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            header = f"# Paper Search: {args.query}\n\n"
            header += f"Source: {args.source} | Results: {len(papers)} | Sort: {args.sort}\n\n"
            out_path.write_text(header + to_markdown_detail(papers), encoding="utf-8")
            print(f"\n[Saved] {out_path}", file=sys.stderr)

        if args.bibtex:
            bib_path = Path(args.bibtex)
            bib_path.parent.mkdir(parents=True, exist_ok=True)
            bib_path.write_text(to_bibtex(papers), encoding="utf-8")
            print(f"[Saved BibTeX] {bib_path}", file=sys.stderr)

    elif args.command == "lookup":
        paper = None
        if args.arxiv:
            paper = lookup_arxiv_id(args.arxiv)
        elif args.doi:
            paper = lookup_doi(args.doi)
        else:
            print("[Error] Provide --arxiv or --doi", file=sys.stderr)
            sys.exit(1)

        if paper:
            print(to_markdown_detail([paper]))
        else:
            print("[Error] Paper not found.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
