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
license: "unknown"
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
