# =============================================================
# КРОК 4 — Навчання моделей
# =============================================================
# Що робить цей файл:
#   Навчає дві ML моделі на матрицях з кроку 3.
#
# Вхідні дані (data/processed/ і models/):
#   - content_matrix.npz     — події × теги
#   - interaction_matrix.npz — юзери × події з Jaccard scores
#   - encoders.pkl           — маппінги індексів
#
# Модель 1 — Content-based (cosine similarity):
#   Рахує схожість між усіма парами тренувальних подій.
#   Результат: матриця 5086 × 5086 де кожне число = наскільки схожі дві події.
#   Зберігається в: models/content_model.pkl
#
# Модель 2 — Collaborative Filtering (SVD):
#   Розкладає interaction matrix (юзери × події) на приховані фактори.
#   k=50 означає: кожен юзер і кожна подія описуються 50 числами.
#   Схожі юзери мають близькі вектори → рекомендуємо те що сподобалось схожим.
#   Результат: predicted_scores (869 юзерів × 5086 подій) — передбачені оцінки.
#   Зберігається в: models/collab_model.pkl
#
# Також зберігає:
#   - models/events_data.pkl — теги тренувальних подій для інференсу в продакшені
# =============================================================

import numpy as np
import pickle
import os
from scipy import sparse
from scipy.sparse.linalg import svds
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import ast

# ── Шляхи ──────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
MDL_DIR  = os.path.join(BASE_DIR, "models")

os.makedirs(MDL_DIR, exist_ok=True)

print("=" * 60)
print("  КРОК 4 — Навчання моделей")
print("=" * 60)

# ── 1. Завантаження даних ──────────────────────────────────────
print("\n Завантаження матриць і енкодерів...")

content_matrix     = sparse.load_npz(
    os.path.join(DATA_DIR, "content_matrix.npz")
)
interaction_matrix = sparse.load_npz(
    os.path.join(DATA_DIR, "interaction_matrix.npz")
)

with open(os.path.join(MDL_DIR, "encoders.pkl"), "rb") as f:
    encoders = pickle.load(f)

print(f"  content_matrix:     {content_matrix.shape}")
print(f"  interaction_matrix: {interaction_matrix.shape}")
print(f"  Енкодери завантажено: {list(encoders.keys())}")

# ── 2. Content-based модель (Cosine Similarity) ────────────────
print("\n Навчання content-based моделі...")
print("  Обчислення cosine similarity між подіями...")

# Cosine similarity між усіма парами подій
# content_matrix: 5086 × 13 → similarity: 5086 × 5086
content_sim = cosine_similarity(content_matrix)

print(f"  Розмір similarity матриці: {content_sim.shape}")
print(f"  Min: {content_sim.min():.4f}, "
      f"Max: {content_sim.max():.4f}, "
      f"Mean: {content_sim.mean():.4f}")

# Зберігаємо content модель
content_model = {
    "similarity_matrix": content_sim,
    "event_ids":         encoders["event_ids"],
    "event2idx":         encoders["event2idx"],
}

with open(os.path.join(MDL_DIR, "content_model.pkl"), "wb") as f:
    pickle.dump(content_model, f)

print(f"   content_model.pkl збережено")

# ── 3. Collaborative filtering модель (SVD) ────────────────────
print("\n Навчання collaborative filtering моделі (SVD)...")

# Кількість прихованих факторів
K = 50
print(f"  Кількість латентних факторів: {K}")

# SVD розкладання
# interaction_matrix: 869 × 5086
# U: 869 × K, sigma: K, Vt: K × 5086
print("  Запуск SVD розкладання...")

U, sigma, Vt = svds(
    interaction_matrix.astype(float),
    k=K
)

# Відновлюємо матрицю передбачень
# predicted_ratings: 869 × 5086
sigma_diag      = np.diag(sigma)
predicted_scores = np.dot(np.dot(U, sigma_diag), Vt)

print(f"  U shape:    {U.shape}")
print(f"  sigma shape: {sigma.shape}")
print(f"  Vt shape:   {Vt.shape}")
print(f"  Predicted scores shape: {predicted_scores.shape}")
print(f"  Predicted min: {predicted_scores.min():.4f}, "
      f"max: {predicted_scores.max():.4f}")

# Зберігаємо collab модель
collab_model = {
    "U":               U,
    "sigma":           sigma,
    "Vt":              Vt,
    "predicted_scores": predicted_scores,
    "user_ids":        encoders["user_ids"],
    "event_ids":       encoders["event_ids"],
    "user2idx":        encoders["user2idx"],
    "event2idx":       encoders["event2idx"],
}

with open(os.path.join(MDL_DIR, "collab_model.pkl"), "wb") as f:
    pickle.dump(collab_model, f)

print(f"   collab_model.pkl збережено")

# ── 4. Збереження events_data для інференсу ────────────────────
print("\n Збереження events_data для інференсу...")


events = pd.read_csv(
    os.path.join(DATA_DIR, "events_clean.csv"), encoding="utf-8"
)
events["tags"] = events["tags"].apply(ast.literal_eval)

events_data = {
    "event_id": events["event_id"].tolist(),
    "title":    events["title"].tolist(),
    "tags":     events["tags"].tolist(),
}

with open(os.path.join(MDL_DIR, "events_data.pkl"), "wb") as f:
    pickle.dump(events_data, f)

print(f"   events_data.pkl збережено → {len(events):,} подій")

# ── 5. Фінальна статистика ─────────────────────────────────────
print("\n Фінальна статистика навчання:")
print(f"  Content модель:  {content_sim.shape[0]:,} × "
      f"{content_sim.shape[1]:,} similarity матриця")
print(f"  Collab модель:   SVD з {K} латентними факторами")
print(f"  Events data:     {len(events):,} подій для інференсу")

print("\n" + "=" * 60)
print("   КРОК 4 ПОВНІСТЮ ЗАВЕРШЕНО")
print("  Збережено моделі:")
print("    - models/content_model.pkl")
print("    - models/collab_model.pkl")
print("    - models/events_data.pkl")
print("  Запускай 5_evaluate.py")
print("=" * 60)