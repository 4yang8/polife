#!/bin/bash
set -e

cd "$(dirname "$0")"

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

VLLM_DISABLE_COMPILE=1 PYTHONNOUSERSITE=1 python -m uvicorn Counseling_KOR_2025.main:app \
  --host 0.0.0.0 --port 8000 \
  --ssl-certfile="${SSL_CERT_PATH}" \
  --ssl-keyfile="${SSL_KEY_PATH}"