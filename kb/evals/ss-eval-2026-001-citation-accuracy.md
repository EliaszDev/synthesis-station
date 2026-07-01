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
