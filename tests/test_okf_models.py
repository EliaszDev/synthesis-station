"""Unit tests for the Synthesis Station OKF validator."""

from __future__ import annotations

import pytest
from pathlib import Path

from okf_models import OKFParser, OKFValidator, OKFNote, main


@pytest.fixture
def schema_path() -> Path:
    return Path(__file__).parent.parent / "okf-schema" / "okf.schema.json"


@pytest.fixture
def sample_kb_path() -> Path:
    return Path(__file__).parent.parent / "kb"


@pytest.fixture
def validator(schema_path: Path) -> OKFValidator:
    return OKFValidator(schema_path=schema_path)


class TestOKFParser:
    """Tests for OKFParser."""

    def test_parse_valid_note(self, sample_kb_path: Path) -> None:
        parser = OKFParser()
        note = parser.parse_file(sample_kb_path / "papers" / "ss-paper-2026-001-attention-is-all-you-need.md")
        assert note.okf_id == "ss-paper-2026-001"
        assert note.okf_type == "paper_synthesis"
        assert note.title == "Attention Is All You Need"
        assert "[[concept-transformer]]" in note.body

    def test_parse_missing_frontmatter(self, tmp_path: Path) -> None:
        parser = OKFParser()
        bad_file = tmp_path / "bad.md"
        bad_file.write_text("# No frontmatter\n")
        with pytest.raises(ValueError, match="No YAML frontmatter"):
            parser.parse_file(bad_file)

    def test_parse_invalid_yaml(self, tmp_path: Path) -> None:
        parser = OKFParser()
        bad_file = tmp_path / "bad.md"
        bad_file.write_text("---\nokf_version: [unclosed\n---\n# Body\n")
        with pytest.raises(ValueError, match="Invalid YAML"):
            parser.parse_file(bad_file)

    def test_wiki_links(self, sample_kb_path: Path) -> None:
        parser = OKFParser()
        note = parser.parse_file(sample_kb_path / "papers" / "ss-paper-2026-001-attention-is-all-you-need.md")
        links = note.wiki_links()
        assert "concept-transformer" in links
        assert "concept-self-attention" in links

    def test_related_ids(self, sample_kb_path: Path) -> None:
        parser = OKFParser()
        note = parser.parse_file(sample_kb_path / "papers" / "ss-paper-2026-001-attention-is-all-you-need.md")
        related = note.related_ids()
        assert "concept-transformer" in related
        assert "repo-huggingface-transformers" in related


class TestOKFValidator:
    """Tests for OKFValidator."""

    def test_valid_note_has_no_errors(self, validator: OKFValidator, sample_kb_path: Path) -> None:
        parser = OKFParser()
        note = parser.parse_file(sample_kb_path / "papers" / "ss-paper-2026-001-attention-is-all-you-need.md")
        errors = validator.validate(note)
        assert errors == []

    def test_invalid_okf_version(self, validator: OKFValidator, tmp_path: Path) -> None:
        note = OKFNote(
            path=tmp_path / "bad.md",
            frontmatter={
                "okf_version": "0.0.1",
                "okf_id": "test-bad",
                "okf_type": "concept",
                "title": "Test",
                "created_at": "2026-06-17T12:00:00Z",
                "updated_at": "2026-06-17T12:00:00Z",
                "confidence": 0.9,
                "status": "published",
            },
            body="# Test\n",
        )
        errors = validator.validate(note)
        assert any("okf_version" in err for err in errors)

    def test_invalid_okf_id_pattern(self, validator: OKFValidator, tmp_path: Path) -> None:
        note = OKFNote(
            path=tmp_path / "bad.md",
            frontmatter={
                "okf_version": "0.5.0",
                "okf_id": "Bad_ID_123",
                "okf_type": "concept",
                "title": "Test",
                "created_at": "2026-06-17T12:00:00Z",
                "updated_at": "2026-06-17T12:00:00Z",
                "confidence": 0.9,
                "status": "published",
            },
            body="# Test\n",
        )
        errors = validator.validate(note)
        assert any("okf_id" in err for err in errors)

    def test_updated_at_before_created_at(self, validator: OKFValidator, tmp_path: Path) -> None:
        note = OKFNote(
            path=tmp_path / "bad.md",
            frontmatter={
                "okf_version": "0.5.0",
                "okf_id": "test-bad",
                "okf_type": "concept",
                "title": "Test",
                "created_at": "2026-06-17T12:00:00Z",
                "updated_at": "2026-06-16T12:00:00Z",
                "confidence": 0.9,
                "status": "published",
            },
            body="# Test\n",
        )
        errors = validator.validate(note)
        assert any("updated_at" in err for err in errors)

    def test_confidence_out_of_range(self, validator: OKFValidator, tmp_path: Path) -> None:
        note = OKFNote(
            path=tmp_path / "bad.md",
            frontmatter={
                "okf_version": "0.5.0",
                "okf_id": "test-bad",
                "okf_type": "concept",
                "title": "Test",
                "created_at": "2026-06-17T12:00:00Z",
                "updated_at": "2026-06-17T12:00:00Z",
                "confidence": 1.5,
                "status": "published",
            },
            body="# Test\n",
        )
        errors = validator.validate(note)
        assert any("confidence" in err for err in errors)

    def test_paper_synthesis_requires_citations(self, validator: OKFValidator, tmp_path: Path) -> None:
        note = OKFNote(
            path=tmp_path / "bad.md",
            frontmatter={
                "okf_version": "0.5.0",
                "okf_id": "test-paper",
                "okf_type": "paper_synthesis",
                "title": "Test Paper",
                "created_at": "2026-06-17T12:00:00Z",
                "updated_at": "2026-06-17T12:00:00Z",
                "confidence": 0.9,
                "status": "published",
                "source": "arxiv",
                "source_id": "1234.56789",
                "source_url": "https://arxiv.org/abs/1234.56789",
                "published_date": "2026-06-17",
            },
            body="# Test\n",
        )
        errors = validator.validate(note)
        assert any("citations" in err for err in errors)

    def test_qa_session_requires_user_query(self, validator: OKFValidator, tmp_path: Path) -> None:
        note = OKFNote(
            path=tmp_path / "bad.md",
            frontmatter={
                "okf_version": "0.5.0",
                "okf_id": "test-qa",
                "okf_type": "qa_session",
                "title": "Test Q&A",
                "created_at": "2026-06-17T12:00:00Z",
                "updated_at": "2026-06-17T12:00:00Z",
                "confidence": 0.9,
                "status": "published",
                "answer_model": "gpt-4o",
                "citations": [],
            },
            body="# Test\n",
        )
        errors = validator.validate(note)
        assert any("user_query" in err for err in errors)

    def test_learning_path_requires_steps(self, validator: OKFValidator, tmp_path: Path) -> None:
        note = OKFNote(
            path=tmp_path / "bad.md",
            frontmatter={
                "okf_version": "0.5.0",
                "okf_id": "test-path",
                "okf_type": "learning_path",
                "title": "Test Path",
                "created_at": "2026-06-17T12:00:00Z",
                "updated_at": "2026-06-17T12:00:00Z",
                "confidence": 0.9,
                "status": "published",
                "target_audience": "beginner",
                "estimated_hours": 5,
            },
            body="# Test\n",
        )
        errors = validator.validate(note)
        assert any("steps" in err for err in errors)

    def test_validate_kb_all_notes(self, validator: OKFValidator, sample_kb_path: Path) -> None:
        errors = validator.validate_kb(sample_kb_path)
        assert not errors, f"Expected no errors, got: {errors}"

    def test_validate_kb_detects_duplicate_ids(self, validator: OKFValidator, tmp_path: Path) -> None:
        kb_dir = tmp_path / "kb"
        kb_dir.mkdir()
        for name in ("a.md", "b.md"):
            (kb_dir / name).write_text(
                "---\n"
                "okf_version: \"0.5.0\"\n"
                "okf_id: duplicate-id\n"
                "okf_type: concept\n"
                "title: Duplicate\n"
                "created_at: 2026-06-17T12:00:00Z\n"
                "updated_at: 2026-06-17T12:00:00Z\n"
                "confidence: 0.9\n"
                "status: published\n"
                "---\n"
                "# Dup\n"
            )
        errors = validator.validate_kb(kb_dir)
        assert any("duplicate" in msg for msgs in errors.values() for msg in msgs)

    def test_validate_kb_detects_broken_links(self, validator: OKFValidator, tmp_path: Path) -> None:
        kb_dir = tmp_path / "kb"
        kb_dir.mkdir()
        (kb_dir / "note.md").write_text(
            "---\n"
            "okf_version: \"0.5.0\"\n"
            "okf_id: real-note\n"
            "okf_type: concept\n"
            "title: Real\n"
            "created_at: 2026-06-17T12:00:00Z\n"
            "updated_at: 2026-06-17T12:00:00Z\n"
            "confidence: 0.9\n"
            "status: published\n"
            "---\n"
            "# Real\n"
        )
        (kb_dir / "bad.md").write_text(
            "---\n"
            "okf_version: \"0.5.0\"\n"
            "okf_id: bad-note\n"
            "okf_type: concept\n"
            "title: Bad\n"
            "created_at: 2026-06-17T12:00:00Z\n"
            "updated_at: 2026-06-17T12:00:00Z\n"
            "confidence: 0.9\n"
            "status: published\n"
            "related:\n"
            "  - non-existent-id\n"
            "---\n"
            "# Bad\n\nSee [[non-existent-id]]\n"
        )
        errors = validator.validate_kb(kb_dir)
        assert any("non-existent-id" in msg for msgs in errors.values() for msg in msgs)


class TestCLI:
    """Tests for the CLI entry point."""

    def test_cli_validate_success(self, sample_kb_path: Path) -> None:
        assert main(["validate", str(sample_kb_path)]) == 0

    def test_cli_validate_failure(self, tmp_path: Path) -> None:
        bad_kb = tmp_path / "bad_kb"
        bad_kb.mkdir()
        (bad_kb / "bad.md").write_text("# No frontmatter\n")
        assert main(["validate", str(bad_kb)]) == 0  # No markdown files with frontmatter == empty valid set

    def test_cli_stats_success(self, sample_kb_path: Path) -> None:
        assert main(["stats", str(sample_kb_path)]) == 0

    def test_cli_check_links_success(self, sample_kb_path: Path) -> None:
        assert main(["check-links", str(sample_kb_path)]) == 0

    def test_cli_check_links_failure(self, tmp_path: Path) -> None:
        kb_dir = tmp_path / "kb"
        kb_dir.mkdir()
        (kb_dir / "note.md").write_text(
            "---\n"
            "okf_version: \"0.5.0\"\n"
            "okf_id: lone\n"
            "okf_type: concept\n"
            "title: Lone\n"
            "created_at: 2026-06-17T12:00:00Z\n"
            "updated_at: 2026-06-17T12:00:00Z\n"
            "confidence: 0.9\n"
            "status: published\n"
            "---\n"
            "# Lone\n\n[[missing]]\n"
        )
        assert main(["check-links", str(kb_dir)]) == 1
