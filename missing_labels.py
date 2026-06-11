import pickle, numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 저장된 TF-IDF vectorizer 및 label 데이터 로드
PKL_PATH = "Counseling_KOR_2025/data/tfidf_store.pkl"

with open(PKL_PATH, "rb") as f:
    store = pickle.load(f)

vectorizer = store["vectorizer"]
X = store["X"]
texts = store["texts"]
labels = store["labels"]
all_labels = store["all_labels"]

# 입력 문장과 가장 유사한 상담 label 예측
def classify_label(text: str) -> dict:
    q = vectorizer.transform([text])
    sims = cosine_similarity(q, X)[0]
    idx = int(np.argmax(sims))
    return {
        "pred_label": labels[idx],
        "score": float(sims[idx]),
        "nearest_text": texts[idx],
        "nearest_label": labels[idx],
    }

# 전체 label 목록 반환
def get_all_labels() -> list[str]:
    return list(all_labels)
