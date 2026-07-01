# Synthesis Station

> **OKF-native research synthesizer.** Turn papers, videos, code repositories, and podcasts into structured, machine-readable knowledge files.

[![OKF Schema](https://img.shields.io/badge/OKF-0.5.0-blue)](./okf-schema/OKF_SCHEMA.md)

## What It Does

Synthesis Station ingests research content from public sources and produces **Open Knowledge Format (OKF)** artifacts:

- Every paper → `paper_synthesis` OKF note
- Every video → `video_synthesis` OKF note with timestamps
- Every concept → `concept` OKF note linked into a knowledge graph
- Every question → `qa_session` OKF note with cited answers
- Every learning path → `learning_path` OKF curriculum
- Every evaluation run → `eval_result` OKF artifact

The output is not a chat. It is a **git-trackable, agent-readable knowledge base**.

## Quick Start

```bash
# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Validate the sample knowledge base
python okf_models.py validate kb/

# Print knowledge base stats
python okf_models.py stats kb/

# Check for broken internal links
python okf_models.py check-links kb/

# Ingest a paper (metadata + author stubs)
python arxiv_ingest.py 1706.03762 --output-dir ./kb/papers

# Ingest a paper with PDF download + LLM synthesis
# Requires Ollama running locally OR an OpenAI/Anthropic API key
python arxiv_ingest.py 1706.03762 --synthesize --output-dir ./kb/papers
```

## OKF Schema

See [okf-schema/OKF_SCHEMA.md](./okf-schema/OKF_SCHEMA.md) for the full specification.

## Knowledge Base Layout

```
kb/
├── papers/      # Paper syntheses
├── videos/      # Video summaries
├── concepts/    # Knowledge graph nodes
├── people/      # Authors, speakers, maintainers
├── repos/       # GitHub repo syntheses
├── datasets/    # Dataset notes
├── qa/          # Persistent Q&A sessions
├── paths/       # Learning paths
├── evals/       # Evaluation results
└── claims/      # Atomic source claims
```

## Tech Stack

| Layer | Tool |
|-------|------|
| Orchestration | LangGraph |
| RAG | LlamaIndex + pgvector |
| Ingestion | arXiv API, GitHub API, RSS |
| PDF Parsing | PyMuPDF |
| LLM Router | LiteLLM (Ollama + OpenAI/Anthropic fallback) |
| Evals | Ragas + LLM-as-a-judge |
| LLMOps | Weights & Biases / MLflow |
| Schema | hermes-okf v0.5.0 |

## License

MIT
