#!/bin/bash
# Example: run Synthesis Station with various AI compute providers.
#
# Usage:
#   export OPENAI_API_KEY="..." && ./examples/run_with_provider.sh 1706.03762
#   export MOONSHOT_API_KEY="..." && ./examples/run_with_provider.sh 1706.03762 --api-model moonshot/kimi-k2-6

set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

ARXIV_ID="${1:-1706.03762}"
shift || true

python arxiv_ingest.py "$ARXIV_ID" \
  --synthesize \
  --output-dir ./kb/papers \
  --download-pdf \
  "$@"
