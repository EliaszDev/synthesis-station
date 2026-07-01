#!/usr/bin/env python3
"""
Synthesis Station arXiv ingest demo.

Fetches a paper from the arXiv API and writes a paper_synthesis OKF note.

Usage:
    python arxiv_ingest.py 1706.03762
    python arxiv_ingest.py 1706.03762 --output-dir ./kb/papers

Requires:
    pip install requests pyyaml
"""

from __future__ import annotations

import argparse
import re
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
import yaml


ARXIV_API_URL = "http://export.arxiv.org/api/query"
OKF_ID_PATTERN = re.compile(r"[^a-z0-9-]+")


def fetch_arxiv_paper(arxiv_id: str) -> dict[str, Any]:
    """Fetch paper metadata from the arXiv Atom API."""
    params = {"id_list": arxiv_id}
    response = requests.get(ARXIV_API_URL, params=params, timeout=30)
    response.raise_for_status()
    return parse_atom(response.text)


def parse_atom(atom_xml: str) -> dict[str, Any]:
    """Extract the first paper from arXiv Atom XML."""
    import xml.etree.ElementTree as ET

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    root = ET.fromstring(atom_xml)
    entry = root.find("atom:entry", ns)
    if entry is None:
        raise ValueError("No paper found in arXiv response")

    title = _get_text(entry, "atom:title", ns)
    summary = _get_text(entry, "atom:summary", ns)
    published = _get_text(entry, "atom:published", ns)
    updated = _get_text(entry, "atom:updated", ns)
    authors = [author.find("atom:name", ns).text for author in entry.findall("atom:author", ns) if author.find("atom:name", ns) is not None]
    categories = [cat.get("term") for cat in entry.findall("atom:category", ns) if cat.get("term")]
    doi = _get_text(entry, "arxiv:doi", ns) or None

    links = entry.findall("atom:link", ns)
    pdf_url = None
    abs_url = None
    for link in links:
        rel = link.get("rel")
        href = link.get("href")
        if rel == "alternate" and href:
            abs_url = href
        if link.get("title") == "pdf" and href:
            pdf_url = href

    return {
        "title": title,
        "summary": summary,
        "published": published,
        "updated": updated,
        "authors": authors,
        "categories": categories,
        "doi": doi,
        "abs_url": abs_url,
        "pdf_url": pdf_url,
    }


def _get_text(element, path: str, ns: dict[str, str]) -> str:
    child = element.find(path, ns)
    return (child.text or "").strip() if child is not None else ""


def make_okf_id(arxiv_id: str) -> str:
    """Generate a stable OKF id from an arXiv id."""
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    normalized = OKF_ID_PATTERN.sub("-", arxiv_id.lower()).strip("-")
    return f"ss-paper-{today}-{normalized}"


def make_filename(arxiv_id: str, title: str) -> str:
    """Generate a safe filename from the paper title."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    normalized = OKF_ID_PATTERN.sub("-", title.lower()).strip("-")
    return f"{today}-{normalized}.md"


def build_author_okf_id(name: str) -> str:
    """Generate a stable person OKF id from an author name."""
    normalized = OKF_ID_PATTERN.sub("-", name.lower()).strip("-")
    return f"person-{normalized}"


def build_author_stub(name: str) -> str:
    """Generate a minimal person OKF note for an author."""
    okf_id = build_author_okf_id(name)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    frontmatter = {
        "okf_version": "0.5.0",
        "okf_id": okf_id,
        "okf_type": "person",
        "title": name,
        "created_at": now,
        "updated_at": now,
        "confidence": 0.8,
        "status": "published",
        "aliases": [],
        "affiliations": [],
        "role": "researcher",
        "papers": [],
        "talks": [],
        "repos": [],
    }
    body = f"# {name}\n\nAuthor of **[[{okf_id}]]** (stub generated from arXiv ingestion).\n"
    return "---\n" + yaml.safe_dump(frontmatter, sort_keys=False) + "---\n\n" + body


def build_okf_note(arxiv_id: str, paper: dict[str, Any]) -> str:
    """Construct the full OKF markdown string."""
    okf_id = make_okf_id(arxiv_id)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    published_date = paper["published"][:10] if paper["published"] else ""

    author_okf_ids = [build_author_okf_id(name) for name in paper["authors"]]

    frontmatter = {
        "okf_version": "0.5.0",
        "okf_id": okf_id,
        "okf_type": "paper_synthesis",
        "title": paper["title"],
        "created_at": now,
        "updated_at": now,
        "source": "arxiv",
        "source_id": arxiv_id,
        "source_url": paper["abs_url"] or f"https://arxiv.org/abs/{arxiv_id}",
        "confidence": 0.85,
        "status": "published",
        "authors": author_okf_ids,
        "published_date": published_date,
        "arxiv_categories": paper["categories"],
        "concepts": [],
        "methods": [],
        "datasets": [],
        "models": [],
        "metrics": [],
        "key_findings": [],
        "limitations": [],
        "related": [],
        "license": "unknown",
        "citations": [
            {
                "id": "c1",
                "text": paper["summary"][:280] + "..." if len(paper["summary"]) > 280 else paper["summary"],
                "source": paper["abs_url"] or f"https://arxiv.org/abs/{arxiv_id}",
                "source_section": "abstract",
                "source_ref": arxiv_id,
                "confidence": 0.85,
            }
        ],
    }

    body = textwrap.dedent(
        f"""\
        # {paper["title"]}

        ## TL;DR

        {paper["summary"][:500]}{"..." if len(paper["summary"]) > 500 else ""}

        ## Abstract

        {paper["summary"]}

        ## Links

        - arXiv abstract: {paper["abs_url"] or f"https://arxiv.org/abs/{arxiv_id}"}
        - arXiv PDF: {paper["pdf_url"] or f"https://arxiv.org/pdf/{arxiv_id}.pdf"}
        {f"- DOI: {paper['doi']}" if paper["doi"] else ""}

        ## Authors

        {", ".join(paper["authors"])}

        ## Categories

        {", ".join(paper["categories"])}
        """
    )

    return "---\n" + yaml.safe_dump(frontmatter, sort_keys=False) + "---\n\n" + body


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest an arXiv paper into an OKF note")
    parser.add_argument("arxiv_id", help="arXiv paper ID (e.g., 1706.03762)")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./kb/papers"),
        help="Directory to write the OKF note",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the OKF note without writing")
    args = parser.parse_args(argv)

    print(f"Fetching arXiv:{args.arxiv_id} ...")
    paper = fetch_arxiv_paper(args.arxiv_id)
    okf_content = build_okf_note(args.arxiv_id, paper)

    if args.dry_run:
        print(okf_content)
        for author in paper["authors"]:
            print("\n" + "=" * 60 + "\n")
            print(build_author_stub(author))
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    filename = make_filename(args.arxiv_id, paper["title"])
    output_path = args.output_dir / filename
    output_path.write_text(okf_content, encoding="utf-8")
    print(f"Wrote OKF note to {output_path}")

    people_dir = args.output_dir.parent / "people"
    people_dir.mkdir(parents=True, exist_ok=True)
    for author in paper["authors"]:
        author_path = people_dir / f"{build_author_okf_id(author)}.md"
        author_path.write_text(build_author_stub(author), encoding="utf-8")
        print(f"Wrote author stub to {author_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
