#!/bin/bash

set -e

ENV_NAME="cesd_chatbot"
PYTHON_VERSION="3.10"

echo "[1/4] Conda 초기화"
source "$(conda info --base)/etc/profile.d/conda.sh"

echo "[2/4] Conda 환경 확인"
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "이미 존재하는 환경입니다: ${ENV_NAME}"
else
    echo "새 환경을 생성합니다: ${ENV_NAME}"
    conda create -y -n ${ENV_NAME} python=${PYTHON_VERSION}
fi

echo "[3/4] Conda 환경 활성화"
conda activate ${ENV_NAME}

echo "[4/4] requirements.txt 설치"
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "환경 설정 완료"
echo "사용 방법: conda activate ${ENV_NAME}"