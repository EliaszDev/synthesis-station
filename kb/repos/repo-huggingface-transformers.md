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
