# =============================================================
# ПРОДАКШЕН — Гібридна рекомендаційна система (інференс)
# =============================================================
# Що робить цей файл:
#   Завантажує навчені моделі і генерує рекомендації для реальних
#   юзерів і подій з MongoDB.
#
# Вхідні дані (models/):
#   - content_model.pkl  — cosine similarity між тренувальними подіями
#                          (в продакшені не використовується напряму,
#                           content scores рахуються через Jaccard по тегах)
#   - collab_model.pkl   — SVD predicted scores (869 юзерів × 5086 подій)
#   - events_data.pkl    — теги тренувальних подій (міст між SVD і MongoDB)
#   - best_weights.pkl   — оптимальні ваги: content=0.8, collab=0.2
#
# Як працює в продакшені (на реальних MongoDB даних):
#   1. Content score  — Jaccard між інтересами юзера і тегами MongoDB події
#   2. Collab score   — середній SVD score тренувальних подій з такими ж тегами
#                       (міст через теги, бо MongoDB ID ≠ тренувальні ID)
#   3. Hybrid         — 0.8 * content + 0.2 * collab
#   4. Повертає топ-10 подій за спаданням hybrid score
#
# Викликається з: main.py (FastAPI endpoint GET /recommendations/{user_id})
# =============================================================

import numpy as np
import pickle
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MDL_DIR  = os.path.join(BASE_DIR, "models")

# ── Завантаження моделей при старті ───────────────────────────
print("[recommender] Завантаження моделей...")

# content_model — cosine similarity між тренувальними подіями (5086 × 5086)
# використовується під час навчання, але в продакшені
# get_content_scores рахує Jaccard напряму по тегах MongoDB подій
with open(os.path.join(MDL_DIR, "content_model.pkl"), "rb") as f:
    content_model = pickle.load(f)

# collab_model — SVD розкладання interaction matrix (юзери × тренувальні події)
# predicted_scores: 869 юзерів × 5086 тренувальних подій
with open(os.path.join(MDL_DIR, "collab_model.pkl"), "rb") as f:
    collab_model = pickle.load(f)

# events_data — теги тренувальних подій (з event_dataset)
# потрібен щоб зв'язати SVD scores з реальними тегами MongoDB подій
with open(os.path.join(MDL_DIR, "events_data.pkl"), "rb") as f:
    events_data = pickle.load(f)

# ваги гібриду підібрані в 5_evaluate.py: content=0.8, collab=0.2
with open(os.path.join(MDL_DIR, "best_weights.pkl"), "rb") as f:
    best_weights = pickle.load(f)

CONTENT_WEIGHT = best_weights["content_weight"]
COLLAB_WEIGHT  = best_weights["collab_weight"]

print(f"[recommender] Ваги: content={CONTENT_WEIGHT}, collab={COLLAB_WEIGHT}")

# ── Попередній розрахунок collab scores по тегах ──────────────
# Проблема: MongoDB події мають інші ID ніж тренувальні події з event_dataset.
# Рішення: використовуємо теги як міст.
#
# Логіка:
# 1. SVD дає predicted_scores (869 юзерів × 5086 тренувальних подій)
# 2. Середнє по всіх юзерах = "популярність" кожної тренувальної події
# 3. Для кожного тегу рахуємо середнє по всіх тренувальних подіях з цим тегом
# 4. Для MongoDB події беремо середнє collab score її тегів
#
# Результат: MongoDB подія з тегом МУЗИКА отримує collab score =
# "наскільки популярні тренувальні події з тегом МУЗИКА серед юзерів"

_predicted = collab_model["predicted_scores"]    # (n_users × n_train_events)
_avg_event_scores = _predicted.mean(axis=0)      # середнє по всіх юзерах

_tag_score_lists: dict[str, list] = {}
for i, tags in enumerate(events_data["tags"]):
    score = float(_avg_event_scores[i])
    for tag in tags:
        if tag not in _tag_score_lists:
            _tag_score_lists[tag] = []
        _tag_score_lists[tag].append(score)

# середній collab score для кожного тегу
_tag_collab_scores: dict[str, float] = {
    tag: float(np.mean(scores))
    for tag, scores in _tag_score_lists.items()
}

print(f"[recommender] Collab scores по тегах: {_tag_collab_scores}")


# ── Допоміжні функції ──────────────────────────────────────────
def minmax(arr: np.ndarray) -> np.ndarray:
    """Нормалізація масиву до діапазону [0, 1]."""
    rng = arr.max() - arr.min()
    return (arr - arr.min()) / rng if rng > 0 else arr


def get_content_scores(
    user_interests: list[str],
    mongo_events: list[dict]
) -> np.ndarray:
    """
    Content-based scores через Jaccard similarity.
    Порівнює інтереси юзера з тегами кожної MongoDB події.

    Jaccard = |перетин| / |об'єднання|
    Чим більше спільних тегів — тим вищий score.
    """
    interests = set(user_interests)
    scores    = np.zeros(len(mongo_events))

    for i, event in enumerate(mongo_events):
        tags    = set(event.get("tags", []))
        overlap = interests & tags
        union   = interests | tags
        if union:
            scores[i] = len(overlap) / len(union)

    return scores


def get_collab_scores(mongo_events: list[dict]) -> np.ndarray:
    """
    Collaborative filtering scores на основі SVD predicted_scores.

    Для кожної MongoDB події:
    - беремо її теги
    - для кожного тегу беремо середній SVD score тренувальних подій з цим тегом
    - усереднюємо по всіх тегах події

    Це дає сигнал: "наскільки популярні події такого типу серед схожих юзерів"
    """
    scores = np.zeros(len(mongo_events))

    for i, event in enumerate(mongo_events):
        tags = event.get("tags", [])
        if not tags:
            continue
        tag_scores = [_tag_collab_scores.get(tag, 0.0) for tag in tags]
        scores[i] = float(np.mean(tag_scores))

    return scores


def get_recommendations(
    user_interests: list[str],
    user_id: str,
    mongo_events: list[dict],
    top_n: int = 10
) -> list[dict]:
    """
    Гібридна рекомендація: content (80%) + collaborative (20%).

    Кроки:
    1. Фільтруємо події які юзер сам створив
    2. Рахуємо content score (Jaccard: інтереси юзера vs теги події)
    3. Рахуємо collab score (SVD: популярність типу події серед схожих юзерів)
    4. Нормалізуємо обидва scores до [0, 1]
    5. Hybrid = 0.8 * content + 0.2 * collab
    6. Повертаємо топ-N за спаданням
    """
    if not mongo_events:
        return []

    # не рекомендуємо юзеру його власні події
    mongo_events = [
        e for e in mongo_events
        if e.get("userId", {}).get("_id", "") != user_id
    ]

    if not mongo_events:
        return []

    # якщо юзер не вибрав інтереси — повертаємо найпопулярніші по кількості учасників
    if not user_interests:
        sorted_events = sorted(
            mongo_events,
            key=lambda e: len(e.get("participants", [])),
            reverse=True
        )
        return sorted_events[:top_n]

    c_scores = get_content_scores(user_interests, mongo_events)
    f_scores = get_collab_scores(mongo_events)

    # нормалізація до [0, 1] щоб обидва scores були на одній шкалі
    c_scores = minmax(c_scores)
    f_scores = minmax(f_scores)

    hybrid = CONTENT_WEIGHT * c_scores + COLLAB_WEIGHT * f_scores

    top_indices = np.argsort(hybrid)[::-1][:top_n]
    return [mongo_events[i] for i in top_indices]
