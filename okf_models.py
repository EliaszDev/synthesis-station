"""
Synthesis Station OKF Parser / Validator

Parses markdown files with YAML frontmatter, validates them against the
Synthesis Station OKF JSON Schema, and checks cross-references within the
knowledge base.

Usage:
    python okf-models.py validate kb/
    python okf-models.py stats kb/
    python okf-models.py check-links kb/
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft7Validator, ValidationError


SCHEMA_PATH = Path(__file__).parent / "okf-schema" / "okf.schema.json"

OKF_ID_PATTERN = re.compile(r"^[a-z0-9-]+$")
WIKI_LINK_PATTERN = re.compile(r"\[\[([a-z0-9-]+)\]\]")


@dataclass(frozen=True)
class OKFNote:
    """A parsed OKF note."""

    path: Path
    frontmatter: dict[str, Any]
    body: str

    @property
    def okf_id(self) -> str | None:
        return self.frontmatter.get("okf_id")

    @property
    def okf_type(self) -> str | None:
        return self.frontmatter.get("okf_type")

    @property
    def title(self) -> str | None:
        return self.frontmatter.get("title")

    @property
    def confidence(self) -> float | None:
        return self.frontmatter.get("confidence")

    @property
    def status(self) -> str | None:
        return self.frontmatter.get("status")

    def wiki_links(self) -> set[str]:
        return set(WIKI_LINK_PATTERN.findall(self.body))

    def related_ids(self) -> set[str]:
        """Return all OKF IDs referenced in the frontmatter (related, concepts, etc.)."""
        ids: set[str] = set()
        for key in ("related", "authors", "concepts", "datasets", "models", "related_concepts", "related_papers", "related_videos", "related_repos", "papers", "talks", "repos", "prerequisites"):
            value = self.frontmatter.get(key)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        ids.add(item)
                    elif isinstance(item, dict) and "okf_id" in item:
                        ids.add(item["okf_id"])
        # learning_path steps reference resources by okf_id
        steps = self.frontmatter.get("steps", [])
        if isinstance(steps, list):
            for step in steps:
                if isinstance(step, dict):
                    resource = step.get("resource")
                    if isinstance(resource, str):
                        ids.add(resource)
        # qa_session retrieved_sources
        sources = self.frontmatter.get("retrieved_sources", [])
        if isinstance(sources, list):
            for src in sources:
                if isinstance(src, dict) and "okf_id" in src:
                    ids.add(src["okf_id"])
        # source_claim used_in
        used_in = self.frontmatter.get("used_in", [])
        if isinstance(used_in, list):
            ids.update(used_in)
        return {okf_id for okf_id in ids if okf_id and OKF_ID_PATTERN.match(okf_id)}


class OKFParser:
    """Parse OKF markdown files."""

    FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)

    def parse_file(self, path: Path) -> OKFNote:
        text = path.read_text(encoding="utf-8")
        match = self.FRONTMATTER_RE.match(text)
        if not match:
            raise ValueError(f"No YAML frontmatter found in {path}")
        try:
            frontmatter = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML frontmatter in {path}: {exc}")
        body = match.group(2)
        return OKFNote(path=path, frontmatter=frontmatter, body=body)

    def parse_directory(self, directory: Path) -> list[OKFNote]:
        notes: list[OKFNote] = []
        for path in sorted(directory.rglob("*.md")):
            if path.name == "index.md":
                continue
            try:
                notes.append(self.parse_file(path))
            except ValueError as exc:
                print(f"[WARN] {exc}", file=sys.stderr)
        return notes


class OKFValidator:
    """Validate OKF notes against the JSON schema and cross-references."""

    def __init__(self, schema_path: Path | None = None) -> None:
        self.schema_path = schema_path or SCHEMA_PATH
        self.schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
        self._validator = Draft7Validator(self.schema)

    def validate(self, note: OKFNote) -> list[str]:
        errors: list[str] = []
        # JSON schema validation
        for err in self._validator.iter_errors(note.frontmatter):
            errors.append(f"schema: {err.message} at {'/'.join(map(str, err.path))}")

        # Custom semantic checks
        okf_id = note.okf_id
        if okf_id and not OKF_ID_PATTERN.match(okf_id):
            errors.append(f"okf_id '{okf_id}' must match {OKF_ID_PATTERN.pattern}")

        created_at = note.frontmatter.get("created_at")
        updated_at = note.frontmatter.get("updated_at")
        if created_at and updated_at and updated_at < created_at:
            errors.append("updated_at must be >= created_at")

        confidence = note.confidence
        if confidence is not None and not (0.0 <= confidence <= 1.0):
            errors.append(f"confidence {confidence} out of range [0.0, 1.0]")

        return errors

    def validate_kb(self, directory: Path) -> dict[str, list[str]]:
        parser = OKFParser()
        notes = parser.parse_directory(directory)
        all_errors: dict[str, list[str]] = {}

        # Build id -> path map
        id_map: dict[str, Path] = {}
        for note in notes:
            okf_id = note.okf_id
            if okf_id:
                if okf_id in id_map:
                    all_errors.setdefault(str(note.path), []).append(
                        f"duplicate okf_id '{okf_id}' (also in {id_map[okf_id]})"
                    )
                else:
                    id_map[okf_id] = note.path

        # Schema + semantic validation
        for note in notes:
            errors = self.validate(note)
            if errors:
                all_errors.setdefault(str(note.path), []).extend(errors)

        # Cross-reference validation
        for note in notes:
            for related_id in note.related_ids():
                if related_id not in id_map:
                    all_errors.setdefault(str(note.path), []).append(
                        f"broken related reference: '{related_id}'"
                    )
            for link in note.wiki_links():
                if link not in id_map:
                    all_errors.setdefault(str(note.path), []).append(
                        f"broken wiki-link: '[[{link}]]'"
                    )

        return all_errors


def validate_kb(directory: Path, schema_path: Path | None = None) -> bool:
    """Validate an entire knowledge base. Return True if no errors."""
    validator = OKFValidator(schema_path=schema_path)
    errors = validator.validate_kb(directory)

    if not errors:
        print(f"✅ Knowledge base '{directory}' is valid.")
        return True

    print(f"❌ Knowledge base '{directory}' has {len(errors)} file(s) with errors:\n")
    for path, msgs in sorted(errors.items()):
        print(f"  {path}")
        for msg in msgs:
            print(f"    - {msg}")
    print()
    return False


def kb_stats(directory: Path) -> None:
    """Print statistics about the knowledge base."""
    parser = OKFParser()
    notes = parser.parse_directory(directory)

    type_counts: dict[str, int] = {}
    total_citations = 0
    total_links = 0
    for note in notes:
        note_type = note.okf_type or "unknown"
        type_counts[note_type] = type_counts.get(note_type, 0) + 1
        total_citations += len(note.frontmatter.get("citations", []))
        total_links += len(note.wiki_links()) + len(note.related_ids())

    print(f"Knowledge base: {directory}")
    print(f"Total notes: {len(notes)}")
    print("Notes by type:")
    for note_type, count in sorted(type_counts.items()):
        print(f"  {note_type}: {count}")
    print(f"Total citations: {total_citations}")
    print(f"Total internal links: {total_links}")


def check_links(directory: Path) -> bool:
    """Check for broken internal links."""
    parser = OKFParser()
    notes = parser.parse_directory(directory)
    id_map = {note.okf_id: note.path for note in notes if note.okf_id}

    broken = 0
    for note in notes:
        for link in note.wiki_links():
            if link not in id_map:
                print(f"  {note.path}: broken wiki-link [[{link}]]")
                broken += 1
        for related_id in note.related_ids():
            if related_id not in id_map:
                print(f"  {note.path}: broken related reference {related_id}")
                broken += 1

    if broken == 0:
        print(f"✅ All internal links in '{directory}' are valid.")
        return True
    print(f"❌ Found {broken} broken link(s) in '{directory}'.")
    return False


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synthesis Station OKF tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate all OKF files in a directory")
    validate_parser.add_argument("directory", type=Path, help="path to knowledge base directory")
    validate_parser.add_argument("--schema", type=Path, default=None, help="path to JSON schema")

    stats_parser = subparsers.add_parser("stats", help="print knowledge base statistics")
    stats_parser.add_argument("directory", type=Path, help="path to knowledge base directory")

    links_parser = subparsers.add_parser("check-links", help="check internal links")
    links_parser.add_argument("directory", type=Path, help="path to knowledge base directory")

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        return 0 if validate_kb(args.directory, schema_path=args.schema) else 1
    if args.command == "stats":
        kb_stats(args.directory)
        return 0
    if args.command == "check-links":
        return 0 if check_links(args.directory) else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
