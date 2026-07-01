"""PDF download and text extraction for Synthesis Station."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import fitz  # pymupdf
import requests


ARXIV_PDF_URL = "https://arxiv.org/pdf/{arxiv_id}.pdf"


def download_pdf(arxiv_id: str, output_dir: Path) -> Path:
    """Download an arXiv PDF to the output directory."""
    url = ARXIV_PDF_URL.format(arxiv_id=arxiv_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{arxiv_id}.pdf"

    response = requests.get(url, timeout=60)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return output_path


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract all text from a PDF file using PyMuPDF."""
    doc = fitz.open(pdf_path)
    try:
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        return "\n".join(text_parts)
    finally:
        doc.close()


def extract_pages_from_pdf(pdf_path: Path) -> list[dict[str, Any]]:
    """Extract text per page with basic metadata."""
    doc = fitz.open(pdf_path)
    try:
        pages = []
        for i, page in enumerate(doc, start=1):
            pages.append({
                "page_number": i,
                "text": page.get_text(),
            })
        return pages
    finally:
        doc.close()
