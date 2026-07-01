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
license: "unknown"
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
