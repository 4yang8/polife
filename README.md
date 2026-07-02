# Counseling KOR Docker Runbook

Docker Compose로 실행하기 전에 아래 준비를 먼저 끝내야 합니다.

## 1. Required Files

프로젝트 루트에 다음 파일/디렉터리가 있어야 합니다.

```text
.env
ssl/ssl.crt
ssl/ssl.key.pem
models/CESD_detector_ver2/
models/cesd_freq/
models/persona_no_history.ckpt
data/counsel_prompt.yaml
data/exploration_paraphrased_with_score.jsonl
```

`.env`는 `.env.example`을 복사해서 만듭니다.

```bash
cp .env.example .env
```

실제 API key, Hugging Face token, 포트, cache 경로는 `.env`에서 설정합니다.

`models/persona_no_history.ckpt`는 PersonaExtractor가 직접 로드하는 checkpoint입니다. 파일 크기가 커서 `models/`는 gitignore 처리되어 있으며, 새 서버/새 clone에서는 이 파일을 별도로 복사해 두어야 합니다.

## 2. Hugging Face Cache

이 프로젝트는 Docker 이미지 안에 Llama/KoBART 모델을 넣지 않습니다. 대신 호스트의 Hugging Face cache를 컨테이너에 마운트합니다.

권장 cache 위치:

```bash
/home/yeajinmin/.cache/huggingface
```

`.env`에는 아래처럼 설정합니다.

```env
HF_HOME=/root/.cache/huggingface
HOST_HF_CACHE_DIR=/home/yeajinmin/.cache/huggingface
```

컨테이너 안에서는 `/root/.cache/huggingface`로 보이고, 실제 파일은 호스트의 `/home/yeajinmin/.cache/huggingface`를 사용합니다.

## 3. Download Models

먼저 Hugging Face token을 준비합니다. Llama 3.1은 gated model이므로 Hugging Face 웹에서 `meta-llama/Llama-3.1-8B-Instruct` 접근 승인이 되어 있어야 합니다.

```bash
cd /home/yeajinmin/Counseling_KOR_2025_docker_try1

export HF_HOME=/home/yeajinmin/.cache/huggingface
export HF_TOKEN=$(grep '^HF_TOKEN=' .env | cut -d= -f2-)
```

Llama 모델을 받습니다. `original/*`는 Transformers 실행에 필요하지 않아서 제외합니다.

```bash
hf download meta-llama/Llama-3.1-8B-Instruct \
  --exclude "original/*" \
  --token "$HF_TOKEN"
```

PersonaExtractor에서 쓰는 KoBART 모델도 받습니다.

```bash
hf download gogamza/kobart-base-v2
```

Llama snapshot 경로를 확인합니다.

```bash
find /home/yeajinmin/.cache/huggingface/hub/models--meta-llama--Llama-3.1-8B-Instruct/snapshots \
  -maxdepth 1 -mindepth 1 -type d
```

출력된 snapshot id를 `.env`의 `LLAMA_MODEL_PATH`에 넣습니다. 컨테이너 내부 경로 기준으로 적어야 합니다.

```env
LLAMA_MODEL_PATH=/root/.cache/huggingface/hub/models--meta-llama--Llama-3.1-8B-Instruct/snapshots/<snapshot-id>
```

## 4. Important .env Keys

| Key | Purpose |
| --- | --- |
| `API_TOKEN` | `main` API의 보호 엔드포인트 인증용 Bearer token |
| `POSTECH_GPT_API` | OpenAI-compatible 후처리/외부 GPT 호출용 key |
| `UNIST_GPT_API` | `unist` summary 서비스의 GPT 호출용 key |
| `HF_TOKEN` | Hugging Face gated model 다운로드/로드용 token |
| `HF_LOCAL_FILES_ONLY` | `1`이면 실행 중 Hugging Face에서 새로 다운로드하지 않음 |
| `LLAMA_MODEL_PATH` | 컨테이너 내부 Llama snapshot 경로 |
| `PERSONA_MODEL_NAME` | PersonaExtractor base model repo id |
| `PERSONA_DEVICE` | PersonaExtractor가 사용할 CUDA device |
| `LLAMA_DEVICE` | 로컬 실행 시 Llama LoRA 모델이 사용할 CUDA device |
| `DOCKER_LLAMA_DEVICE` | Docker 실행 시 컨테이너 내부 CUDA device |
| `VLLM_API_BASE` | 로컬 실행 시 vLLM API base URL |
| `DOCKER_VLLM_API_BASE` | Docker 실행 시 `main` 컨테이너가 호출할 vLLM API base URL |
| `UNIST_API_BASE` | 로컬 실행 시 UNIST API URL |
| `DOCKER_UNIST_API_BASE` | Docker 네트워크에서 `main -> unist` 호출 URL. 보통 `http://unist:8001` |
| `SSL_CERT_PATH` | 컨테이너 내부 SSL certificate path |
| `SSL_KEY_PATH` | 컨테이너 내부 SSL key path |
| `HOST_SSL_DIR` | 호스트 SSL 디렉터리 |
| `CONTAINER_SSL_DIR` | 컨테이너 SSL 마운트 경로 |
| `HOST_LOGS_DIR` | 호스트 로그 디렉터리 |
| `LOG_DIR` | 컨테이너 내부 로그 경로 |
| `HOST_HF_CACHE_DIR` | 호스트 Hugging Face cache 경로 |
| `HF_HOME` | 컨테이너 내부 Hugging Face cache 경로 |
| `MAIN_HOST_PORT` | 호스트에서 main API로 접근할 포트 |
| `UNIST_HOST_PORT` | 호스트에서 unist API로 접근할 포트 |

Docker Compose 내부 통신에서는 `DOCKER_*` 값이 중요합니다.

예를 들어 `main` 컨테이너가 `unist` 컨테이너를 부를 때는:

```env
DOCKER_UNIST_API_BASE=http://unist:8001
```

vLLM 서버가 원격 서버에 있다면:

```env
DOCKER_VLLM_API_BASE=http://141.223.163.135:9000/v1
```

vLLM 서버가 호스트 머신의 `localhost:9000`에 있다면:

```env
DOCKER_VLLM_API_BASE=http://host.docker.internal:9000/v1
```

## 5. GPU Setting

현재 Compose 설정은 호스트 GPU `1`번만 컨테이너에 넘기고, 컨테이너 내부에서는 `cuda:0`으로 사용합니다.

```yaml
device_ids: ["1"]
```

따라서 `.env`는 아래처럼 둡니다.

```env
DOCKER_LLAMA_DEVICE=cuda:0
PERSONA_DEVICE=cuda:0
```

컨테이너 안에서 확인:

```bash
docker compose exec main python -c "import torch; print(torch.cuda.device_count()); print(torch.cuda.get_device_name(0))"
```

## 6. Build And Run

처음 실행 또는 코드 변경 후:

```bash
docker compose build
docker compose up -d
```

`model.py`, `persona.py`, `main.py`처럼 `main` 서비스 코드만 바뀐 경우:

```bash
docker compose build main
docker compose up -d
```

로그 확인:

```bash
docker compose logs -f main
```

## 7. Smoke Test

`main` API는 HTTPS로 뜹니다.

```bash
curl -k -X POST "https://localhost:18000/chat/chat1" \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "docker-test-001",
    "text": "안녕하세요.",
    "image": null
  }'
```

Swagger UI:

```text
https://localhost:18000/docs
```

`unist` API:

```text
http://localhost:18001/docs
```

## 8. Common Checks

vLLM 연결 확인:

```bash
docker compose exec main curl --max-time 5 "$VLLM_API_BASE/models"
```

호스트 cache 확인:

```bash
du -sh /home/yeajinmin/.cache/huggingface
```

Llama safetensors 확인:

```bash
find /home/yeajinmin/.cache/huggingface/hub/models--meta-llama--Llama-3.1-8B-Instruct/snapshots \
  -name 'model-*.safetensors' -printf '%f\n' | sort
```

Docker compose 설정 확인:

```bash
docker compose config --quiet
```
