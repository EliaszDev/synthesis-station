#!/usr/bin/env python3
"""
Synthesis Station arXiv ingest pipeline.

Fetches paper metadata, optionally downloads the PDF, and synthesizes
structured OKF notes with local or API LLM fallback.

Usage:
    python arxiv_ingest.py 1706.03762
    python arxiv_ingest.py 1706.03762 --synthesize --output-dir ./kb/papers
    python arxiv_ingest.py 1706.03762 --local-model ollama/llama3.1 --api-model gpt-4o-mini

Requires:
    pip install requests pyyaml pymupdf litellm
"""

from __future__ import annotations

import argparse
import re
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import yaml

from synthesis.llm import SynthesisLLM, SynthesisResult
from synthesis.pdf import download_pdf, extract_text_from_pdf


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
    authors = [
        author.find("atom:name", ns).text
        for author in entry.findall("atom:author", ns)
        if author.find("atom:name", ns) is not None
    ]
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


def build_concept_okf_id(concept: str) -> str:
    """Generate a stable concept OKF id from a concept string."""
    normalized = OKF_ID_PATTERN.sub("-", concept.lower()).strip("-")
    return f"concept-{normalized}"


def build_concept_stub(concept: str) -> str:
    """Generate a minimal concept OKF note for an extracted concept."""
    okf_id = build_concept_okf_id(concept)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    frontmatter = {
        "okf_version": "0.5.0",
        "okf_id": okf_id,
        "okf_type": "concept",
        "title": concept,
        "created_at": now,
        "updated_at": now,
        "confidence": 0.8,
        "status": "published",
        "concept_type": "technique",
        "related_concepts": [],
        "related_papers": [],
        "related_repos": [],
    }
    body = f"# {concept}\n\nConcept extracted from paper synthesis. See **[[{okf_id}]]**.\n"
    return "---\n" + yaml.safe_dump(frontmatter, sort_keys=False) + "---\n\n" + body


def build_okf_note(
    arxiv_id: str,
    paper: dict[str, Any],
    synthesis: SynthesisResult | None = None,
) -> str:
    """Construct the full OKF markdown string, optionally enriched with synthesis."""
    okf_id = make_okf_id(arxiv_id)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    published_date = paper["published"][:10] if paper["published"] else ""

    author_okf_ids = [build_author_okf_id(name) for name in paper["authors"]]
    concept_okf_ids = []
    if synthesis and synthesis.concepts:
        concept_okf_ids = [build_concept_okf_id(c) for c in synthesis.concepts]

    confidence = 0.85 if synthesis is None else 0.75
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
        "confidence": confidence,
        "status": "published",
        "authors": author_okf_ids,
        "published_date": published_date,
        "arxiv_categories": paper["categories"],
        "concepts": concept_okf_ids,
        "methods": synthesis.methods if synthesis else [],
        "datasets": synthesis.datasets if synthesis else [],
        "models": synthesis.models if synthesis else [],
        "metrics": synthesis.metrics if synthesis else [],
        "key_findings": synthesis.key_findings if synthesis else [],
        "limitations": synthesis.limitations if synthesis else [],
        "related": synthesis.related if synthesis else [],
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

    synthesis_section = ""
    if synthesis:
        findings = "\n".join(f"- {f}" for f in synthesis.key_findings)
        methods = "\n".join(f"- {m}" for m in synthesis.methods)
        limitations = "\n".join(f"- {l}" for l in synthesis.limitations)
        synthesis_section = textwrap.dedent(
            f"""\

            ## Synthesis Summary

            {synthesis.summary}

            ## Key Findings

            {findings}

            ## Methods

            {methods}

            ## Limitations

            {limitations}
            """
        )

    body = textwrap.dedent(
        f"""\
        # {paper["title"]}

        ## TL;DR

        {paper["summary"][:500]}{"..." if len(paper["summary"]) > 500 else ""}
        {synthesis_section}

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
    parser = argparse.ArgumentParser(
        description="Ingest an arXiv paper into an OKF note"
    )
    parser.add_argument("arxiv_id", help="arXiv paper ID (e.g., 1706.03762)")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./kb/papers"),
        help="Directory to write the OKF note",
    )
    parser.add_argument(
        "--synthesize",
        action="store_true",
        help="Download PDF and run LLM synthesis",
    )
    parser.add_argument(
        "--download-pdf",
        action="store_true",
        help="Keep the downloaded PDF in the output directory",
    )
    parser.add_argument(
        "--local-model",
        default="ollama/llama3.1",
        help="Local model identifier via LiteLLM",
    )
    parser.add_argument(
        "--api-model",
        default="openai/gpt-4o-mini",
        help="API model identifier via LiteLLM (e.g., openai/gpt-4o-mini, moonshot/kimi-k2-6, anthropic/claude-3-5-sonnet)",
    )
    parser.add_argument(
        "--no-authors",
        action="store_true",
        help="Skip writing author stub notes",
    )
    parser.add_argument(
        "--no-concepts",
        action="store_true",
        help="Skip writing concept stub notes",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the OKF note without writing",
    )
    args = parser.parse_args(argv)

    print(f"Fetching arXiv:{args.arxiv_id} ...")
    paper = fetch_arxiv_paper(args.arxiv_id)

    synthesis = None
    if args.synthesize:
        print("Downloading PDF...")
        pdf_path = download_pdf(args.arxiv_id, args.output_dir)
        print(f"Downloaded PDF to {pdf_path}")

        print("Extracting text from PDF...")
        pdf_text = extract_text_from_pdf(pdf_path)

        print("Synthesizing with LLM...")
        llm = SynthesisLLM(
            local_model=args.local_model,
            api_model=args.api_model,
        )
        synthesis = llm.synthesize_paper(pdf_text)

        if not args.download_pdf:
            pdf_path.unlink()

    okf_content = build_okf_note(args.arxiv_id, paper, synthesis)

    if args.dry_run:
        print(okf_content)
        if not args.no_authors:
            for author in paper["authors"]:
                print("\n" + "=" * 60 + "\n")
                print(build_author_stub(author))
        if not args.no_concepts and synthesis:
            for concept in synthesis.concepts:
                print("\n" + "=" * 60 + "\n")
                print(build_concept_stub(concept))
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    filename = make_filename(args.arxiv_id, paper["title"])
    output_path = args.output_dir / filename
    output_path.write_text(okf_content, encoding="utf-8")
    print(f"Wrote OKF note to {output_path}")

    if not args.no_authors:
        people_dir = args.output_dir.parent / "people"
        people_dir.mkdir(parents=True, exist_ok=True)
        for author in paper["authors"]:
            author_path = people_dir / f"{build_author_okf_id(author)}.md"
            author_path.write_text(build_author_stub(author), encoding="utf-8")
            print(f"Wrote author stub to {author_path}")

    if not args.no_concepts and synthesis:
        concepts_dir = args.output_dir.parent / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        for concept in synthesis.concepts:
            concept_path = concepts_dir / f"{build_concept_okf_id(concept)}.md"
            concept_path.write_text(build_concept_stub(concept), encoding="utf-8")
            print(f"Wrote concept stub to {concept_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
