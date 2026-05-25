# =============================================================
# КРОК 3 — Feature Engineering (побудова матриць)
# =============================================================
# Що робить цей файл:
#   Перетворює очищені дані на числові матриці для ML моделей.
#
# Вхідні дані (data/processed/):
#   - events_clean.csv, users_clean.csv, interactions_clean.csv (з кроку 2)
#
# Що будує:
#   1. content_matrix (події × теги)
#      Кожна подія представлена як вектор з 0 і 1 по 13 тегах.
#      Наприклад: подія [МУЗИКА, ВЕЧІР] → [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
#      Використовується для cosine similarity між подіями (content модель).
#
#   2. interaction_matrix (юзери × події)
#      Таблиця з Jaccard scores — наскільки кожен юзер підходить кожній події.
#      Використовується для SVD (collab модель).
#
#   3. train/test split (80/20 по юзерах)
#      80% юзерів → навчання моделі
#      20% юзерів → перевірка якості в кроці 5
#
#   4. encoders.pkl — маппінги event_id/user_id → індекс в матриці
#
# Виходить (data/processed/):
#   - content_matrix.npz        — sparse матриця подій
#   - interaction_matrix.npz    — sparse матриця взаємодій (тільки train)
#   - train_interactions.csv
#   - test_interactions.csv
# Виходить (models/):
#   - encoders.pkl              — mlb, event2idx, user2idx, event_ids, user_ids
# =============================================================

import pandas as pd
import numpy as np
import ast
import os
import pickle
from scipy import sparse
from sklearn.preprocessing import MultiLabelBinarizer

# ── Шляхи ──────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IN_DIR   = os.path.join(BASE_DIR, "data", "processed")
OUT_DIR  = os.path.join(BASE_DIR, "data", "processed")
MDL_DIR  = os.path.join(BASE_DIR, "models")

os.makedirs(MDL_DIR, exist_ok=True)

print("=" * 60)
print("  КРОК 3 — Feature Engineering")
print("=" * 60)

# ── 1. Завантаження даних ──────────────────────────────────────
print("\n Завантаження очищених файлів...")

events = pd.read_csv(
    os.path.join(IN_DIR, "events_clean.csv"), encoding="utf-8"
)
users = pd.read_csv(
    os.path.join(IN_DIR, "users_clean.csv"), encoding="utf-8"
)
interactions = pd.read_csv(
    os.path.join(IN_DIR, "interactions_clean.csv"), encoding="utf-8"
)

# Парсинг тегів
events["tags"]     = events["tags"].apply(ast.literal_eval)
users["interests"] = users["interests"].apply(ast.literal_eval)

print(f"  events:       {len(events):>6,} рядків")
print(f"  users:        {len(users):>6,} рядків")
print(f"  interactions: {len(interactions):>6,} рядків")

# ── 2. Content матриця (MultiLabelBinarizer) ───────────────────
print("\n Побудова content матриці (події × теги)...")

mlb = MultiLabelBinarizer()
content_matrix = mlb.fit_transform(events["tags"])

print(f"  Розмір матриці: {content_matrix.shape}")
print(f"  Теги: {list(mlb.classes_)}")

# Зберігаємо як sparse матрицю
content_sparse = sparse.csr_matrix(content_matrix)
sparse.save_npz(
    os.path.join(OUT_DIR, "content_matrix.npz"),
    content_sparse
)
print(f"   content_matrix.npz збережено")

# ── 3. Індекси для маппингу ────────────────────────────────────
print("\n Побудова індексів...")

# event_id → індекс рядка в матриці
event_ids   = events["event_id"].tolist()
event2idx   = {eid: idx for idx, eid in enumerate(event_ids)}

# user_id → індекс рядка в interaction матриці
user_ids    = users["user_id"].tolist()
user2idx    = {uid: idx for idx, uid in enumerate(user_ids)}

print(f"  Унікальних подій: {len(event2idx):,}")
print(f"  Унікальних юзерів: {len(user2idx):,}")

# ── 4. Train/test split (80/20 по юзерах) ─────────────────────
print("\n  Train/test split (80/20 по юзерах)...")

np.random.seed(42)
all_users    = users["user_id"].tolist()
n_test       = int(len(all_users) * 0.2)
test_users   = set(np.random.choice(all_users, size=n_test, replace=False))
train_users  = set(all_users) - test_users

train_inter  = interactions[interactions["user_id"].isin(train_users)]
test_inter   = interactions[interactions["user_id"].isin(test_users)]

print(f"  Train юзерів:     {len(train_users):,}")
print(f"  Test юзерів:      {len(test_users):,}")
print(f"  Train взаємодій:  {len(train_inter):,}")
print(f"  Test взаємодій:   {len(test_inter):,}")

# Зберігаємо train/test
train_inter.to_csv(
    os.path.join(OUT_DIR, "train_interactions.csv"),
    index=False, encoding="utf-8"
)
test_inter.to_csv(
    os.path.join(OUT_DIR, "test_interactions.csv"),
    index=False, encoding="utf-8"
)
print(f"   train_interactions.csv і test_interactions.csv збережено")

# ── 5. Interaction матриця (scipy sparse) ──────────────────────
print("\n Побудова interaction матриці (юзери × події)...")

n_users  = len(user_ids)
n_events = len(event_ids)

# Будуємо sparse матрицю з train взаємодій
rows, cols, data = [], [], []
for _, row in train_inter.iterrows():
    uid = row["user_id"]
    eid = row["event_id"]
    if uid in user2idx and eid in event2idx:
        rows.append(user2idx[uid])
        cols.append(event2idx[eid])
        data.append(row["score"])

interaction_matrix = sparse.csr_matrix(
    (data, (rows, cols)),
    shape=(n_users, n_events)
)

print(f"  Розмір матриці: {interaction_matrix.shape}")
print(f"  Ненульових елементів: {interaction_matrix.nnz:,}")
print(f"  Density: {interaction_matrix.nnz / (n_users * n_events) * 100:.4f}%")

sparse.save_npz(
    os.path.join(OUT_DIR, "interaction_matrix.npz"),
    interaction_matrix
)
print(f"   interaction_matrix.npz збережено")

# ── 6. Збереження енкодерів ────────────────────────────────────
print("\n Збереження енкодерів...")

encoders = {
    "mlb":        mlb,
    "event2idx":  event2idx,
    "user2idx":   user2idx,
    "event_ids":  event_ids,
    "user_ids":   user_ids,
}

with open(os.path.join(MDL_DIR, "encoders.pkl"), "wb") as f:
    pickle.dump(encoders, f)

print(f"   encoders.pkl збережено")

# ── 7. Фінальна статистика ─────────────────────────────────────
print("\n Фінальна статистика:")
print(f"  Content матриця:     {content_matrix.shape[0]:,} подій × "
      f"{content_matrix.shape[1]} тегів")
print(f"  Interaction матриця: {interaction_matrix.shape[0]:,} юзерів × "
      f"{interaction_matrix.shape[1]:,} подій")
print(f"  Train взаємодій:     {len(train_inter):,}")
print(f"  Test взаємодій:      {len(test_inter):,}")

print("\n" + "=" * 60)
print("   КРОК 3 ПОВНІСТЮ ЗАВЕРШЕНО")
print("  Запускай 4_train_model.py")
print("=" * 60)