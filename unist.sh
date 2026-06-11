#!/bin/bash

python -m uvicorn Counseling_KOR_2025.unist:app \
  --host 0.0.0.0 \
  --port 8001