import numpy as np
import pandas as pd
import pickle
import os
import ast

# ── Шляхи ──────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
MDL_DIR  = os.path.join(BASE_DIR, "models")

print("=" * 60)
print("  КРОК 5 — Оцінка якості моделей")
print("=" * 60)

# ── 1. Завантаження моделей і даних ───────────────────────────
print("\nЗавантаження моделей...")

with open(os.path.join(MDL_DIR, "content_model.pkl"), "rb") as f:
    content_model = pickle.load(f)

with open(os.path.join(MDL_DIR, "collab_model.pkl"), "rb") as f:
    collab_model = pickle.load(f)

with open(os.path.join(MDL_DIR, "events_data.pkl"), "rb") as f:
    events_data = pickle.load(f)

test_inter = pd.read_csv(
    os.path.join(DATA_DIR, "test_interactions.csv"),
    encoding="utf-8"
)
users_clean = pd.read_csv(
    os.path.join(DATA_DIR, "users_clean.csv"),
    encoding="utf-8"
)

users_clean["interests"] = users_clean["interests"].apply(
    ast.literal_eval
)

print(f"  content_model завантажено ")
print(f"  collab_model завантажено  ")
print(f"  Тестових взаємодій: {len(test_inter):,}")
print(f"  Тестових юзерів:    {test_inter['user_id'].nunique():,}")

# ── 2. Функції для генерації рекомендацій ─────────────────────
def get_content_scores(user_interests, event2idx, similarity_matrix):
    """Content-based score для юзера через його інтереси."""
    n_events = similarity_matrix.shape[0]
    scores   = np.zeros(n_events)

    # Знаходимо події які відповідають інтересам юзера
    # через теги з events_data
    for idx, tags in enumerate(events_data["tags"]):
        overlap = len(set(user_interests) & set(tags))
        if overlap > 0:
            union   = len(set(user_interests) | set(tags))
            jaccard = overlap / union
            # Поширюємо score через similarity матрицю
            scores += jaccard * similarity_matrix[idx]

    return scores

def get_collab_scores(user_id, user2idx, predicted_scores):
    """Collaborative score для юзера з predicted матриці."""
    if user_id not in user2idx:
        return np.zeros(predicted_scores.shape[1])
    user_idx = user2idx[user_id]
    return predicted_scores[user_idx]

def get_hybrid_recommendations(
    user_id, user_interests,
    content_weight, collab_weight,
    top_n=10
):
    """Гібридні рекомендації для юзера."""
    event2idx        = content_model["event2idx"]
    similarity_matrix = content_model["similarity_matrix"]
    user2idx         = collab_model["user2idx"]
    predicted_scores = collab_model["predicted_scores"]

    # Content і collab scores
    c_scores = get_content_scores(
        user_interests, event2idx, similarity_matrix
    )
    f_scores = get_collab_scores(
        user_id, user2idx, predicted_scores
    )

    # Нормалізація до [0, 1]
    def minmax(arr):
        rng = arr.max() - arr.min()
        return (arr - arr.min()) / rng if rng > 0 else arr

    c_scores = minmax(c_scores)
    f_scores = minmax(f_scores)

    # Гібридний score
    hybrid = content_weight * c_scores + collab_weight * f_scores

    # Топ-N індексів
    top_indices  = np.argsort(hybrid)[::-1][:top_n]
    top_event_ids = [events_data["event_id"][i] for i in top_indices]

    return top_event_ids

# ── 3. Оцінка метрик ──────────────────────────────────────────
def evaluate(content_weight, collab_weight, top_n=10):
    """Precision@K, Recall@K, Coverage для заданих ваг."""
    precisions  = []
    recalls     = []
    recommended = set()

    test_users = test_inter["user_id"].unique()

    test_grouped = (
        test_inter
        .groupby("user_id")["event_id"]
        .apply(set)
        .to_dict()
    )
    user_interests_map = (
        users_clean
        .set_index("user_id")["interests"]
        .to_dict()
    )

    for user_id in test_users:
        # Реальні взаємодії юзера в тесті
        actual = test_grouped.get(user_id, set())
        if not actual:
            continue

        # Інтереси юзера
        interests = user_interests_map.get(user_id)
        if interests is None:
            continue

        # Рекомендації
        recs = get_hybrid_recommendations(
            user_id, interests,
            content_weight, collab_weight,
            top_n=top_n
        )

        recommended.update(recs)

        # Precision@K і Recall@K
        hits       = len(set(recs) & actual)
        precisions.append(hits / top_n)
        recalls.append(hits / len(actual))

    precision = np.mean(precisions)
    recall    = np.mean(recalls)
    coverage  = len(recommended) / len(events_data["event_id"])

    return precision, recall, coverage

# ── 4. Підбір ваг ─────────────────────────────────────────────
print("\n Підбір оптимальних ваг гібриду...")
print(f"  {'Ваги (c/f)':<15} {'Precision@10':<15} "
      f"{'Recall@10':<15} {'Coverage':<10}")
print("  " + "-" * 55)

weight_combinations = [
    (1.0, 0.0),
    (0.8, 0.2),
    (0.7, 0.3),
    (0.6, 0.4),
    (0.5, 0.5),
    (0.3, 0.7),
    (0.0, 1.0),
]

results = []
for cw, fw in weight_combinations:
    p, r, cov = evaluate(cw, fw)
    results.append((cw, fw, p, r, cov))
    print(f"  {cw:.1f}/{fw:.1f}{'':>9} "
          f"{p:.4f}{'':>9} "
          f"{r:.4f}{'':>9} "
          f"{cov:.4f}")

# ── 5. Найкраща комбінація ────────────────────────────────────
print("\n Найкраща комбінація за Precision@10:")
best = max(results, key=lambda x: x[2])
print(f"  Content weight: {best[0]:.1f}")
print(f"  Collab weight:  {best[1]:.1f}")
print(f"  Precision@10:   {best[2]:.4f}")
print(f"  Recall@10:      {best[3]:.4f}")
print(f"  Coverage:       {best[4]:.4f}")

# Зберігаємо найкращі ваги
best_weights = {
    "content_weight": best[0],
    "collab_weight":  best[1],
}
with open(os.path.join(MDL_DIR, "best_weights.pkl"), "wb") as f:
    pickle.dump(best_weights, f)

print(f"\n   best_weights.pkl збережено")

print("\n" + "=" * 60)
print("   КРОК 5 ПОВНІСТЮ ЗАВЕРШЕНО")
print("  ML пайплайн завершено!")
print("  Запускай main.py для FastAPI сервісу")
print("=" * 60)