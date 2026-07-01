# Synthesis Station OKF Schema v0.5.0

> OKF (Open Knowledge Format) output specification for Synthesis Station — a multimodal research synthesizer that turns papers, videos, code, and podcasts into structured, agent-readable knowledge files.

---

## 1. Design Principles

1. **Every synthesis output is a file.** Chat is ephemeral; files are durable.
2. **YAML frontmatter carries machine metadata.** Markdown body carries human-readable content.
3. **Everything is linkable.** Notes connect via `[[wiki-links]]` and `okf_id` references.
4. **Provenance is mandatory.** Every claim must be traceable to a source.
5. **Git-friendly.** Diffs should be meaningful and reviewable.
6. **Agent-readable.** LLM agents and tools can consume these files without special parsers.

---

## 2. Global OKF Frontmatter Fields

Every Synthesis Station `.md` file MUST include these core fields:

```yaml
---
okf_version: "0.5.0"
okf_id: "ss-2026-001"          # Globally unique within the knowledge base
okf_type: "paper_synthesis"      # One of the types defined below
title: "Attention Is All You Need"
created_at: "2026-06-17T12:00:00Z"
updated_at: "2026-06-17T12:00:00Z"
source: "arxiv"                  # Origin system / API
source_id: "1706.03762"          # ID in the source system
source_url: "https://arxiv.org/abs/1706.03762"
confidence: 0.94                 # 0.0–1.0, system-assessed reliability
status: "published"              # draft | published | deprecated | superseded
authors:                         # OKF IDs of person notes
  - "person-vaswani-ashish"
  - "person-shazeer-noam"
tags:
  - "transformers"
  - "nlp"
  - "self-attention"
related:                         # OKF IDs of related notes
  - "ss-2026-042"
  - "concept-transformer"
license: "unknown"               # from source where applicable
---
```

---

## 3. OKF Note Types

### 3.1 `paper_synthesis`

Synthesized output from an arXiv/paper source.

```yaml
---
okf_version: "0.5.0"
okf_id: "ss-paper-2026-001"
okf_type: "paper_synthesis"
title: "Attention Is All You Need"
created_at: "2026-06-17T12:00:00Z"
updated_at: "2026-06-17T12:00:00Z"
source: "arxiv"
source_id: "1706.03762"
source_url: "https://arxiv.org/abs/1706.03762"
confidence: 0.94
status: "published"
authors:
  - "person-vaswani-ashish"
  - "person-shazeer-noam"
  - "person-parmar-niki"
  - "person-uszkoreit-jakob"
  - "person-jones-llion"
  - "person-gomez-aidan"
  - "person-kaiser-lukasz"
  - "person-polosukhin-illia"
published_date: "2017-06-12"
arxiv_categories:
  - "cs.CL"
  - "cs.LG"
concepts:
  - "concept-transformer"
  - "concept-self-attention"
  - "concept-positional-encoding"
  - "concept-multi-head-attention"
methods:
  - "Scaled Dot-Product Attention"
  - "Multi-Head Attention"
  - "Positional Encoding"
datasets:
  - "dataset-wmt14-en-de"
  - "dataset-wmt14-en-fr"
models:
  - "model-transformer-base"
  - "model-transformer-big"
metrics:
  - "BLEU"
  - "training-time"
key_findings:
  - "The Transformer achieves state-of-the-art translation quality while being more parallelizable."
  - "Self-attention reduces path length between any two positions to O(1)."
limitations:
  - "Quadratic complexity in sequence length."
  - "No built-in inductive bias for recurrence or convolution."
related:
  - "ss-video-2026-015"
  - "concept-transformer"
  - "repo-huggingface-transformers"
citations:
  - id: "c1"
    text: "The Transformer is the first transduction model based entirely on attention."
    source: "https://arxiv.org/abs/1706.03762"
    source_section: "abstract"
    source_ref: "1706.03762"
    confidence: 0.98
  - id: "c2"
    text: "Self-attention can be computed in parallel across all positions."
    source: "https://arxiv.org/pdf/1706.03762.pdf"
    source_section: "3.2"
    source_ref: "1706.03762"
    confidence: 0.95
---

# Attention Is All You Need

## TL;DR

Introduced the Transformer, a sequence transduction model replacing recurrence and convolution with self-attention. Achieves SOTA on WMT 2014 English-to-German and English-to-French translation.

## Problem

RNNs and CNNs struggle with long-range dependencies or require sequential computation that limits parallelization.

## Method

The model uses **[[concept-self-attention]]** and **[[concept-multi-head-attention]]** with **[[concept-positional-encoding]]** to inject order information.

## Results

| Task | BLEU | Training Time |
|------|------|---------------|
| WMT14 En→De | 28.4 | 12 hours on 8 P100s |
| WMT14 En→Fr | 41.0 | 3.5 days on 8 P100s |

## Limitations

- [[limitation-quadratic-attention]]
- [[limitation-no-recurrence-bias]]

## Related Notes

- [[concept-transformer]]
- [[repo-huggingface-transformers]]
- [[ss-video-2026-015]]
```

---

### 3.2 `video_synthesis`

Synthesized output from a YouTube/video source.

```yaml
---
okf_version: "0.5.0"
okf_id: "ss-video-2026-015"
okf_type: "video_synthesis"
title: "Transformers Explained by Jay Alammar"
created_at: "2026-06-17T12:00:00Z"
updated_at: "2026-06-17T12:00:00Z"
source: "youtube"
source_id: "xz-k7Y9wK6o"
source_url: "https://www.youtube.com/watch?v=xz-k7Y9wK6o"
confidence: 0.91
status: "published"
channel: "Jay Alammar"
published_date: "2019-12-01"
duration_seconds: 1187
language: "en"
formats_available:
  - "transcript"
  - "key_frames"
  - "summary"
concepts:
  - "concept-transformer"
  - "concept-self-attention"
  - "concept-encoder-decoder"
related:
  - "ss-paper-2026-001"
  - "concept-transformer"
citations:
  - id: "c1"
    text: "The encoder processes the input sequence and the decoder generates the output sequence."
    source: "https://www.youtube.com/watch?v=xz-k7Y9wK6o"
    source_section: "05:23"
    confidence: 0.92
---

# Transformers Explained by Jay Alammar

## Summary

A visual, intuitive walkthrough of the Transformer architecture. Covers encoder-decoder structure, self-attention, multi-head attention, and positional encoding.

## Key Timestamps

| Time | Topic |
|------|-------|
| 01:15 | Why sequence-to-sequence models matter |
| 05:23 | Encoder-decoder overview |
| 12:40 | Self-attention calculation |
| 22:10 | Multi-head attention |

## Related Notes

- [[ss-paper-2026-001]]
- [[concept-transformer]]
```

---

### 3.3 `concept`

A knowledge graph node for a concept, model, technique, or term.

```yaml
---
okf_version: "0.5.0"
okf_id: "concept-transformer"
okf_type: "concept"
title: "Transformer (Architecture)"
created_at: "2026-06-17T12:00:00Z"
updated_at: "2026-06-17T12:00:00Z"
confidence: 0.99
status: "published"
aliases:
  - "Transformer model"
  - "Attention-based architecture"
concept_type: "model_architecture"  # model_architecture | technique | metric | dataset | problem
related_concepts:
  - "concept-self-attention"
  - "concept-multi-head-attention"
  - "concept-positional-encoding"
  - "concept-encoder-decoder"
related_papers:
  - "ss-paper-2026-001"
related_videos:
  - "ss-video-2026-015"
related_repos:
  - "repo-huggingface-transformers"
---

# Transformer (Architecture)

## Definition

A deep learning architecture introduced in 2017 that uses **[[concept-self-attention]]** to weigh the influence of different input tokens, replacing recurrence and convolution.

## Intuition

Instead of reading a sentence word-by-word like an RNN, the Transformer looks at every word at once and decides which words are relevant to each other.

## Key Components

- [[concept-self-attention]]
- [[concept-multi-head-attention]]
- [[concept-positional-encoding]]
- [[concept-feed-forward-networks]]

## Applications

- Machine translation
- Text generation
- Vision transformers (ViT)
- Multimodal models

## Learn More

- [[ss-paper-2026-001]]
- [[ss-video-2026-015]]
```

---

### 3.4 `person`

A researcher, author, speaker, or maintainer.

```yaml
---
okf_version: "0.5.0"
okf_id: "person-vaswani-ashish"
okf_type: "person"
title: "Ashish Vaswani"
created_at: "2026-06-17T12:00:00Z"
updated_at: "2026-06-17T12:00:00Z"
confidence: 0.95
status: "published"
aliases:
  - "A. Vaswani"
affiliations:
  - "Google Brain"
  - "Adept AI"
  - "Essential AI"
role: "researcher"
orcid: "0000-0000-0000-0000"
scholar_url: "https://scholar.google.com/citations?user=..."
papers:
  - "ss-paper-2026-001"
talks: []
repos: []
---

# Ashish Vaswani

First author of **[[ss-paper-2026-001]]**. Known for pioneering the Transformer architecture.
```

---

### 3.5 `repo_synthesis`

Synthesized output from a GitHub repository.

```yaml
---
okf_version: "0.5.0"
okf_id: "repo-huggingface-transformers"
okf_type: "repo_synthesis"
title: "huggingface/transformers"
created_at: "2026-06-17T12:00:00Z"
updated_at: "2026-06-17T12:00:00Z"
source: "github"
source_id: "huggingface/transformers"
source_url: "https://github.com/huggingface/transformers"
confidence: 0.93
status: "published"
owner: "huggingface"
repo: "transformers"
language: "Python"
stars: 138000
license: "Apache-2.0"
concepts:
  - "concept-transformer"
  - "concept-bert"
  - "concept-gpt"
key_files:
  - "src/transformers/models/bert/modeling_bert.py"
  - "src/transformers/models/gpt2/modeling_gpt2.py"
related:
  - "ss-paper-2026-001"
  - "concept-bert"
---

# huggingface/transformers

## What It Is

The most widely used library for state-of-the-art transformer models. Provides pretrained models and training utilities for NLP, vision, audio, and multimodal tasks.

## Key Capabilities

- Load pretrained models with `AutoModel`
- Tokenize with `AutoTokenizer`
- Fine-tune with the `Trainer` API
- Export to ONNX, TorchScript

## Usage Example

```python
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")
```
```

---

### 3.6 `dataset`

A dataset note with metadata and usage context.

```yaml
---
okf_version: "0.5.0"
okf_id: "dataset-wmt14-en-de"
okf_type: "dataset"
title: "WMT 2014 English-to-German"
created_at: "2026-06-17T12:00:00Z"
updated_at: "2026-06-17T12:00:00Z"
source: "custom"
source_url: "https://www.statmt.org/wmt14/"
confidence: 0.98
status: "published"
dataset_type: "parallel_text"
languages:
  - "en"
  - "de"
size: "4.5M sentence pairs"
related_papers:
  - "ss-paper-2026-001"
related_concepts:
  - "concept-machine-translation"
---

# WMT 2014 English-to-German

Standard benchmark dataset for machine translation. Used in **[[ss-paper-2026-001]]** to evaluate the Transformer.
```

---

### 3.7 `qa_session`

A user question + synthesized answer, stored as a durable OKF note.

```yaml
---
okf_version: "0.5.0"
okf_id: "ss-qa-2026-003"
okf_type: "qa_session"
title: "How does self-attention differ from cross-attention?"
created_at: "2026-06-17T12:00:00Z"
updated_at: "2026-06-17T12:00:00Z"
confidence: 0.91
status: "published"
user_query: "How does self-attention differ from cross-attention?"
query_embedding_model: "text-embedding-3-large"
retrieved_sources:
  - okf_id: "ss-paper-2026-001"
    score: 0.92
  - okf_id: "concept-self-attention"
    score: 0.88
  - okf_id: "concept-cross-attention"
    score: 0.85
answer_model: "claude-sonnet-4"
answer_type: "explanation"
tone: "beginner"
citations:
  - id: "c1"
    text: "Self-attention relates different positions of a single sequence."
    source: "https://arxiv.org/abs/1706.03762"
    source_ref: "1706.03762"
    confidence: 0.96
  - id: "c2"
    text: "Cross-attention connects the query from the decoder to keys and values from the encoder."
    source: "https://arxiv.org/pdf/1706.03762.pdf"
    source_ref: "1706.03762"
    confidence: 0.94
---

# How does self-attention differ from cross-attention?

## Answer

**Self-attention** computes relationships between all positions in the *same* sequence. In the encoder, every word attends to every other word in the input sentence.

**Cross-attention** computes relationships between a *query* sequence (usually the decoder hidden state) and a *key/value* sequence from the encoder.

## Analogy

Self-attention is like re-reading a sentence and noticing how each word relates to the others. Cross-attention is like a translator checking the original sentence while writing the translation.

## Related Concepts

- [[concept-self-attention]]
- [[concept-cross-attention]]
- [[concept-transformer]]
```

---

### 3.8 `learning_path`

A curated learning path generated for a user.

```yaml
---
okf_version: "0.5.0"
okf_id: "ss-path-2026-001"
okf_type: "learning_path"
title: "Understand Transformers from Scratch"
created_at: "2026-06-17T12:00:00Z"
updated_at: "2026-06-17T12:00:00Z"
confidence: 0.89
status: "published"
target_audience: "mid-level_swe"
estimated_hours: 12
prerequisites:
  - "concept-neural-networks"
  - "concept-backpropagation"
steps:
  - order: 1
    title: "Attention Intuition"
    resource: "ss-video-2026-015"
    type: "video"
  - order: 2
    title: "Read the Original Paper"
    resource: "ss-paper-2026-001"
    type: "paper"
  - order: 3
    title: "Implement Self-Attention in NumPy"
    resource: "repo-attention-from-scratch"
    type: "repo"
  - order: 4
    title: "Fine-tune BERT with Hugging Face"
    resource: "repo-huggingface-transformers"
    type: "repo"
---

# Understand Transformers from Scratch

## Goal

Build an intuitive and practical understanding of the Transformer architecture, from math to fine-tuning.

## Step 1: Attention Intuition

Watch [[ss-video-2026-015]] to build visual intuition.

## Step 2: Read the Original Paper

Study [[ss-paper-2026-001]] for the formal definition and experimental results.

## Step 3: Implement from Scratch

Code [[repo-attention-from-scratch]] to internalize the mechanics.

## Step 4: Fine-tune BERT

Use [[repo-huggingface-transformers]] for a real-world application.
```

---

### 3.9 `eval_result`

Structured evaluation output for a synthesis run.

```yaml
---
okf_version: "0.5.0"
okf_id: "ss-eval-2026-001"
okf_type: "eval_result"
title: "Paper Synthesis Citation Accuracy — 2026-06-17"
created_at: "2026-06-17T12:00:00Z"
updated_at: "2026-06-17T12:00:00Z"
confidence: 0.99
status: "published"
eval_task: "citation_accuracy"
dataset: "ss-eval-citation-v1"
model: "claude-sonnet-4"
prompt_version: "v3.1.2"
metrics:
  citation_precision: 0.91
  citation_recall: 0.88
  faithfulness: 0.86
  answer_relevance: 0.92
samples_evaluated: 100
judge_model: "gpt-4o"
config:
  temperature: 0.3
  max_tokens: 2048
notes: "Improved by adding source_ref normalization to the prompt."
---

# Paper Synthesis Citation Accuracy — 2026-06-17

## Summary

Evaluated 100 generated paper syntheses for citation accuracy and faithfulness. Used an LLM-as-a-judge with a rubric-based scoring system.

## Key Findings

- Citation precision improved 5% after normalizing source references.
- Faithfulness remains the lowest metric; needs better figure/diagram extraction.
```

---

### 3.10 `source_claim`

A single atomic claim extracted from a source, used for citation and verification.

```yaml
---
okf_version: "0.5.0"
okf_id: "ss-claim-2026-0001"
okf_type: "source_claim"
text: "Self-attention allows modeling dependencies without recurrence."
source: "arxiv"
source_id: "1706.03762"
source_url: "https://arxiv.org/abs/1706.03762"
source_section: "abstract"
confidence: 0.98
verified_by: []
contradicted_by: []
used_in:
  - "ss-paper-2026-001"
  - "ss-qa-2026-003"
---
```

---

## 4. Directory Layout

```
synthesis-station-kb/
├── index.md
├── okf.schema.json
├── papers/
│   └── ss-paper-2026-001-attention-is-all-you-need.md
├── videos/
│   └── ss-video-2026-015-transformers-explained.md
├── concepts/
│   ├── concept-transformer.md
│   ├── concept-self-attention.md
│   └── concept-multi-head-attention.md
├── people/
│   ├── person-vaswani-ashish.md
│   └── person-shazeer-noam.md
├── repos/
│   └── repo-huggingface-transformers.md
├── datasets/
│   └── dataset-wmt14-en-de.md
├── qa/
│   └── ss-qa-2026-003-self-vs-cross-attention.md
├── paths/
│   └── ss-path-2026-001-transformers-from-scratch.md
├── evals/
│   └── ss-eval-2026-001-citation-accuracy.md
└── claims/
    └── ss-claim-2026-0001-self-attention-no-recurrence.md
```

---

## 5. Linking Conventions

### 5.1 Wiki-Links

Use `[[okf_id]]` for backlinks within the markdown body:

```markdown
See [[concept-transformer]] for the architecture overview.
```

### 5.2 Citation References

Cite inline with `[^c1]` and link to the `citations` list in frontmatter:

```markdown
The Transformer uses self-attention [^c1].
```

### 5.3 Source Reference Format

Every `citation` MUST include:
- `text`: the exact or paraphrased claim
- `source`: resolvable URL
- `source_ref`: stable identifier (e.g., arXiv ID, DOI, GitHub repo)
- `source_section`: section/timestamp where the claim appears
- `confidence`: 0.0–1.0

---

## 6. Confidence Scoring

| Score | Meaning |
|-------|---------|
| 0.95–1.00 | Direct quote or verbatim extraction from source |
| 0.85–0.94 | Strong paraphrase, well-supported by source |
| 0.70–0.84 | Reasonable inference, may need human review |
| 0.50–0.69 | Speculative, low-evidence claim |
| < 0.50 | Do not publish; flag for review |

---

## 7. Validation Rules

1. `okf_id` must be unique across the knowledge base.
2. `okf_type` must be from the allowed list.
3. `citations` must contain at least one entry for `paper_synthesis`, `video_synthesis`, and `qa_session`.
4. All `related` and `[[wiki-link]]` targets should resolve to existing or stub notes.
5. `source_url` must be a valid URL.
6. `updated_at` must be ≥ `created_at`.

---

## 8. Integration with hermes-okf v0.5.0

This schema extends hermes-okf with:
- A `source_claim` type for atomic, verifiable knowledge
- A `qa_session` type for persistent user-agent interactions
- A `learning_path` type for generated curricula
- Structured `citations` with machine-readable provenance
- Confidence scores on every synthesized note

Hermes-okf tools can consume these files directly for agent memory, retrieval, and long-term context.
