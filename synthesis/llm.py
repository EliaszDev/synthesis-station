"""LLM client for paper synthesis with local + API fallback.

Usage:
    from synthesis.llm import SynthesisLLM

    llm = SynthesisLLM()
    result = llm.synthesize_paper(text)

Priority:
  1. Ollama (local) if running
  2. LiteLLM provider if API key set
  3. Structured failure response if none available
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from litellm import completion


DEFAULT_LOCAL_MODEL = "ollama/llama3.1"
DEFAULT_API_MODEL = "gpt-4o-mini"


PAPER_SYNTHESIS_PROMPT = """\
You are a research assistant. Read the following academic paper text and extract a structured synthesis.

Return ONLY a JSON object with these keys:
- "key_findings": list of 3-5 key findings
- "methods": list of methods/techniques used
- "limitations": list of limitations or weaknesses
- "concepts": list of 5-10 important concepts as simple strings
- "datasets": list of datasets mentioned
- "models": list of model names or architectures mentioned
- "metrics": list of evaluation metrics mentioned
- "related": list of related work titles or arxiv ids if mentioned
- "summary": a 2-3 sentence plain-language summary

Paper text:
{text}
"""


@dataclass
class SynthesisResult:
    """Structured output from LLM synthesis."""

    key_findings: list[str]
    methods: list[str]
    limitations: list[str]
    concepts: list[str]
    datasets: list[str]
    models: list[str]
    metrics: list[str]
    related: list[str]
    summary: str

    @classmethod
    def empty(cls) -> "SynthesisResult":
        return cls(
            key_findings=[],
            methods=[],
            limitations=[],
            concepts=[],
            datasets=[],
            models=[],
            metrics=[],
            related=[],
            summary="",
        )


class SynthesisLLM:
    """LLM client with local-first fallback to API providers."""

    def __init__(
        self,
        local_model: str = DEFAULT_LOCAL_MODEL,
        api_model: str = DEFAULT_API_MODEL,
    ) -> None:
        self.local_model = local_model
        self.api_model = api_model

    def synthesize_paper(self, text: str) -> SynthesisResult:
        """Run synthesis against available models, falling back gracefully."""
        prompt = PAPER_SYNTHESIS_PROMPT.format(text=text[:12000])

        # Try local Ollama first
        if self._is_ollama_available():
            try:
                raw = self._complete(self.local_model, prompt)
                return self._parse(raw)
            except Exception as exc:
                print(f"Local model failed ({exc}), trying API fallback...")

        # Try API model if key is configured
        if self._is_api_available():
            try:
                raw = self._complete(self.api_model, prompt)
                return self._parse(raw)
            except Exception as exc:
                print(f"API model failed ({exc}), returning empty synthesis.")

        return SynthesisResult.empty()

    def _is_ollama_available(self) -> bool:
        """Check if Ollama is running locally."""
        import urllib.request

        try:
            urllib.request.urlopen("http://localhost:11434", timeout=2)
            return True
        except Exception:
            return False

    def _is_api_available(self) -> bool:
        """Check if any LiteLLM-supported API key is configured."""
        return bool(
            os.environ.get("OPENAI_API_KEY")
            or os.environ.get("ANTHROPIC_API_KEY")
            or os.environ.get("MOONSHOT_API_KEY")
            or os.environ.get("LITELLM_API_KEY")
        )

    def _complete(self, model: str, prompt: str) -> str:
        """Call LiteLLM completion and return message content."""
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content

    def _parse(self, raw: str) -> SynthesisResult:
        """Parse JSON response, tolerating markdown fences."""
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```json"):
                lines = lines[1:]
            else:
                lines = lines[1:]
            cleaned = "\n".join(lines)
            if cleaned.endswith("```"):
                cleaned = cleaned[: -len("```")].strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Could not parse synthesis JSON: {exc}") from exc

        return SynthesisResult(
            key_findings=data.get("key_findings", []),
            methods=data.get("methods", []),
            limitations=data.get("limitations", []),
            concepts=data.get("concepts", []),
            datasets=data.get("datasets", []),
            models=data.get("models", []),
            metrics=data.get("metrics", []),
            related=data.get("related", []),
            summary=data.get("summary", ""),
        )
