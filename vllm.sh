/home/yeajinmin/anaconda3/envs/vllm/bin/vllm serve Counseling_KOR_2025/models/exaone_110_maxturn10/merged \
  --host 0.0.0.0 --port 9000 \
  --served-model-name counseling \
  --dtype auto \
  --trust-remote-code \

