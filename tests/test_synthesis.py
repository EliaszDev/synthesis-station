"""Tests for PDF extraction and LLM synthesis modules."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from synthesis.llm import SynthesisLLM, SynthesisResult
from synthesis.pdf import extract_pages_from_pdf, extract_text_from_pdf


def test_extract_text_from_pdf(tmp_path: Path) -> None:
    # Create a minimal PDF programmatically via pymupdf
    import fitz

    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello from the test paper.")
    doc.save(str(pdf_path))
    doc.close()

    text = extract_text_from_pdf(pdf_path)
    assert "Hello from the test paper" in text


def test_extract_pages_from_pdf(tmp_path: Path) -> None:
    import fitz

    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page()
        page.insert_text((50, 50), f"Page {i + 1}")
    doc.save(str(pdf_path))
    doc.close()

    pages = extract_pages_from_pdf(pdf_path)
    assert len(pages) == 3
    assert pages[0]["page_number"] == 1
    assert "Page 1" in pages[0]["text"]


class TestSynthesisLLM:
    """Tests for the LLM synthesis client."""

    def test_parse_raw_json(self) -> None:
        llm = SynthesisLLM()
        raw = json.dumps({
            "key_findings": ["finding one"],
            "methods": ["method one"],
            "limitations": ["limit one"],
            "concepts": ["attention"],
            "datasets": [],
            "models": [],
            "metrics": [],
            "related": [],
            "summary": "A short summary.",
        })
        result = llm._parse(raw)
        assert result.key_findings == ["finding one"]
        assert result.summary == "A short summary."

    def test_parse_markdown_fenced_json(self) -> None:
        llm = SynthesisLLM()
        raw = (
            "```json\n"
            + json.dumps({
                "key_findings": ["kf"],
                "methods": ["m"],
                "limitations": ["l"],
                "concepts": ["c"],
                "datasets": [],
                "models": [],
                "metrics": [],
                "related": [],
                "summary": "s",
            })
            + "\n```"
        )
        result = llm._parse(raw)
        assert result.key_findings == ["kf"]

    def test_parse_invalid_json_raises(self) -> None:
        llm = SynthesisLLM()
        with pytest.raises(ValueError, match="Could not parse synthesis JSON"):
            llm._parse("not valid json")

    def test_synthesize_paper_returns_empty_when_no_model(self) -> None:
        llm = SynthesisLLM()
        with patch.object(llm, "_is_ollama_available", return_value=False), \
             patch.object(llm, "_is_api_available", return_value=False):
            result = llm.synthesize_paper("some paper text")
        assert result == SynthesisResult.empty()

    def test_synthesize_paper_uses_local_model(self) -> None:
        llm = SynthesisLLM()
        expected = SynthesisResult(
            key_findings=["kf"],
            methods=["m"],
            limitations=["l"],
            concepts=["c"],
            datasets=[],
            models=[],
            metrics=[],
            related=[],
            summary="s",
        )
        with patch.object(llm, "_is_ollama_available", return_value=True), \
             patch.object(llm, "_complete", return_value=json.dumps({
                 "key_findings": ["kf"],
                 "methods": ["m"],
                 "limitations": ["l"],
                 "concepts": ["c"],
                 "datasets": [],
                 "models": [],
                 "metrics": [],
                 "related": [],
                 "summary": "s",
             })):
            result = llm.synthesize_paper("text")
        assert result == expected

    def test_synthesize_paper_falls_back_to_api(self) -> None:
        llm = SynthesisLLM()
        with patch.object(llm, "_is_ollama_available", return_value=False), \
             patch.object(llm, "_is_api_available", return_value=True), \
             patch.object(llm, "_complete", return_value=json.dumps({
                 "key_findings": ["api"],
                 "methods": [],
                 "limitations": [],
                 "concepts": [],
                 "datasets": [],
                 "models": [],
                 "metrics": [],
                 "related": [],
                 "summary": "api summary",
             })):
            result = llm.synthesize_paper("text")
        assert result.key_findings == ["api"]
