#!/bin/bash
# Example: run Synthesis Station with a Kimi (Moonshot) API key

export MOONSHOT_API_KEY="your-kimi-api-key-here"

cd "$(dirname "$0")"
source venv/bin/activate

python arxiv_ingest.py 1706.03762 \
  --synthesize \
  --api-model moonshot/kimi-k2-6 \
  --output-dir ./kb/papers \
  --download-pdf
