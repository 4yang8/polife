VLLM_DISABLE_COMPILE=1 PYTHONNOUSERSITE=1 python -m uvicorn Counseling_KOR_2025.main:app \
  --host 0.0.0.0 --port 8000 \
  --ssl-certfile=/home/yeajinmin/ssl/ssl.crt \
  --ssl-keyfile=/home/yeajinmin/ssl/ssl.key.pem
# 실행: /home/username/Counseling_KOR_2025/main.sh