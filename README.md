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
# Validate the sample knowledge base
python okf_models.py validate kb/

# Print knowledge base stats
python okf_models.py stats kb/

# Check for broken internal links
python okf_models.py check-links kb/
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
| Ingestion | arXiv API, YouTube, GitHub API, RSS |
| Multimodal | Whisper, VQA, video-to-text models |
| LLM Router | LiteLLM |
| Evals | Ragas + LLM-as-a-judge |
| LLMOps | Weights & Biases / MLflow |
| Schema | hermes-okf v0.5.0 |

## License

MIT
