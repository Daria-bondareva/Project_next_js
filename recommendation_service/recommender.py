import numpy as np
import pickle
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MDL_DIR  = os.path.join(BASE_DIR, "models")

# ── Завантаження моделей при старті ───────────────────────────
print("[recommender] Завантаження моделей...")

with open(os.path.join(MDL_DIR, "content_model.pkl"), "rb") as f:
    content_model = pickle.load(f)

with open(os.path.join(MDL_DIR, "collab_model_mongodb.pkl"), "rb") as f:
    collab_model = pickle.load(f)

with open(os.path.join(MDL_DIR, "best_weights.pkl"), "rb") as f:
    best_weights = pickle.load(f)

CONTENT_WEIGHT = best_weights["content_weight"]  # 0.8
COLLAB_WEIGHT  = best_weights["collab_weight"]   # 0.2

print(f"[recommender] Ваги: content={CONTENT_WEIGHT}, collab={COLLAB_WEIGHT}")

# ── Допоміжні функції ──────────────────────────────────────────
def minmax(arr: np.ndarray) -> np.ndarray:
    rng = arr.max() - arr.min()
    return (arr - arr.min()) / rng if rng > 0 else arr

def get_content_scores(
    user_interests: list[str],
    mongo_events: list[dict]
) -> np.ndarray:
    """Jaccard similarity між interests юзера і тегами кожної події."""
    interests = set(user_interests)
    scores    = np.zeros(len(mongo_events))

    for i, event in enumerate(mongo_events):
        tags    = set(event.get("tags", []))
        overlap = interests & tags
        union   = interests | tags
        if union:
            scores[i] = len(overlap) / len(union)

    return scores

def get_collab_scores(user_id: str, mongo_events: list[dict]) -> np.ndarray:
    """Collab scores з SVD матриці, навченої на реальних MongoDB participants."""
    scores = np.zeros(len(mongo_events))

    user2idx        = collab_model["user2idx"]
    event2idx       = collab_model["event2idx"]
    predicted_scores = collab_model["predicted_scores"]

    if user_id not in user2idx:
        return scores  # cold-start: юзер не має взаємодій у тренувальних даних

    user_row = predicted_scores[user2idx[user_id]]  # вектор довжиною n_events

    for i, event in enumerate(mongo_events):
        eid = str(event.get("_id", ""))
        if eid in event2idx:
            scores[i] = user_row[event2idx[eid]]

    return scores

def get_recommendations(
    user_interests: list[str],
    user_id: str,
    mongo_events: list[dict],
    top_n: int = 10
) -> list[dict]:
    """Повертає топ-N рекомендованих подій."""
    if not mongo_events:
        return []
    
    # Фільтруємо події які юзер сам створив
    mongo_events = [
        e for e in mongo_events
        if e.get("userId", {}).get("_id", "") != user_id
    ]

    if not mongo_events:
        return []
    
    if not user_interests:
        # Якщо немає інтересів — повертаємо найпопулярніші події
        sorted_events = sorted(
            mongo_events,
            key=lambda e: len(e.get("participants", [])),
            reverse=True
        )
        return sorted_events[:top_n]

    # Content і collab scores
    c_scores = get_content_scores(user_interests, mongo_events)
    f_scores = get_collab_scores(user_id, mongo_events)

    # Нормалізація
    c_scores = minmax(c_scores)
    f_scores = minmax(f_scores)

    # Гібридний score
    hybrid = CONTENT_WEIGHT * c_scores + COLLAB_WEIGHT * f_scores

    # Топ-N індексів
    top_indices = np.argsort(hybrid)[::-1][:top_n]

    return [mongo_events[i] for i in top_indices]