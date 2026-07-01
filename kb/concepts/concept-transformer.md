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
concept_type: "model_architecture"
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
