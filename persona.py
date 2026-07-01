import os
import pytorch_lightning as pl
from transformers import BartForConditionalGeneration, AutoTokenizer
import argparse
from dotenv import load_dotenv

load_dotenv()

HF_LOCAL_FILES_ONLY = os.getenv("HF_LOCAL_FILES_ONLY", "1").lower() in ("1", "true", "yes", "on")
if HF_LOCAL_FILES_ONLY:
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

PERSONA_MODEL_NAME = os.getenv("PERSONA_MODEL_NAME", "gogamza/kobart-base-v2")
PERSONA_MODEL_PATH = os.getenv("PERSONA_MODEL_PATH")
PERSONA_DEVICE = os.getenv("PERSONA_DEVICE", os.getenv("LLAMA_DEVICE", "cuda:0"))


def resolve_persona_model_path(model_dir_or_name: str) -> str:
    if PERSONA_MODEL_PATH:
        if HF_LOCAL_FILES_ONLY and not os.path.isdir(PERSONA_MODEL_PATH):
            raise FileNotFoundError(f"PERSONA_MODEL_PATH does not exist: {PERSONA_MODEL_PATH}")
        return PERSONA_MODEL_PATH
    return model_dir_or_name

# KoBART 기반 persona 추출 모델을 LightningModule 형태로 감싸는 클래스
class LitModel(pl.LightningModule):
    def __init__(self, learning_rate, tokenizer, model, total_steps=0, context_window=5):
        super().__init__()
        self.tokenizer = tokenizer
        self.model = model
        self.learning_rate = learning_rate
        self.test_loss = []
        self.total_steps = total_steps
        self.context_window = context_window

# 사용자 발화에서 persona 정보를 추출하는 클래스
class PersonaExtractor:
    _instance = None  # 싱글톤 인스턴스 저장

    # 모델이 여러 번 로드되지 않도록 싱글톤 방식으로 인스턴스 생성
    def __new__(cls, model_dir_or_name=PERSONA_MODEL_NAME):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(model_dir_or_name)
        return cls._instance

    # tokenizer와 persona extraction 모델 로드
    def _initialize(self, model_dir_or_name):
        print("Loading model and tokenizer...")
        model_path = resolve_persona_model_path(model_dir_or_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=HF_LOCAL_FILES_ONLY)
        bart_model = BartForConditionalGeneration.from_pretrained(model_path, local_files_only=HF_LOCAL_FILES_ONLY)

        # Add special tokens
        self.tokenizer.add_special_tokens({'additional_special_tokens': ["<persona>", "<No persona>"]})
        bart_model.resize_token_embeddings(len(self.tokenizer))

        self.model = LitModel.load_from_checkpoint(
            "Counseling_KOR_2025/models/persona_no_history.ckpt",
            learning_rate=1e-5,
            tokenizer=self.tokenizer,
            model=bart_model,
            map_location = "cpu"
        )
        self.model.to(PERSONA_DEVICE)
        self.model.eval()
        print("Model and tokenizer loaded successfully!")
    
    # 입력 문장에서 persona 정보를 생성
    def predict_persona(self, input_text, eval_beams=5, max_new_tokens=128):

        # Tokenize input
        inputs = self.tokenizer(input_text, return_tensors="pt", max_length=256, truncation=True).to(PERSONA_DEVICE)

        # Generate persona text
        outputs = self.model.model.generate(
            inputs['input_ids'],
            max_new_tokens=max_new_tokens,
            num_beams=eval_beams,
            early_stopping=False,
            no_repeat_ngram_size=2,
            eos_token_id=self.tokenizer.eos_token_id,
            repetition_penalty=1.2,
            temperature=1.0
        )

        generated_persona = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        generated_persona = generated_persona.replace("鈐", "").strip()

        return generated_persona if len(generated_persona.strip()) > 10 else ""

if __name__ == '__main__':
    PersonaExtractor()  # 한 번만 초기화
