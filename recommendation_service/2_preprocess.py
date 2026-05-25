# =============================================================
# КРОК 2 — Препроцесинг
# =============================================================
# Що робить цей файл:
#   Очищає дані після кроку 1 і готує їх до навчання моделі.
#
# Вхідні дані (data/processed/):
#   - events.csv, users.csv, interactions.csv  (з кроку 1)
#
# Що робить:
#   1. Видаляє дублікати (одна подія/юзер може бути кілька разів)
#   2. Видаляє рядки з пропущеними значеннями
#   3. Парсить теги і інтереси зі строк у списки Python
#   4. Фільтрація холодного старту — видаляє юзерів і події
#      у яких менше 3 взаємодій (їх не можна навчити добре)
#   5. Перевіряє консистентність — залишає тільки юзерів і події
#      які присутні в interactions
#
# Виходить (data/processed/):
#   - events_clean.csv        — очищені події
#   - users_clean.csv         — очищені юзери
#   - interactions_clean.csv  — очищені взаємодії
# =============================================================

import pandas as pd
import ast
import os

# ── Шляхи ──────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IN_DIR   = os.path.join(BASE_DIR, "data", "processed")
OUT_DIR  = os.path.join(BASE_DIR, "data", "processed")

print("=" * 60)
print("  КРОК 2 — Препроцесинг")
print("=" * 60)

# ── 1. Завантаження даних ──────────────────────────────────────
print("\n Завантаження файлів...")

events = pd.read_csv(
    os.path.join(IN_DIR, "events.csv"), encoding="utf-8"
)
users = pd.read_csv(
    os.path.join(IN_DIR, "users.csv"), encoding="utf-8"
)
interactions = pd.read_csv(
    os.path.join(IN_DIR, "interactions.csv"), encoding="utf-8"
)

print(f"  events:       {len(events):>7,} рядків")
print(f"  users:        {len(users):>7,} рядків")
print(f"  interactions: {len(interactions):>7,} рядків")

# ── 2. Перевірка дублікатів ────────────────────────────────────
print("\n Перевірка дублікатів...")

events_dups       = events.duplicated(subset=["event_id"]).sum()
users_dups        = users.duplicated(subset=["user_id"]).sum()
interactions_dups = interactions.duplicated(
    subset=["user_id", "event_id"]
).sum()

print(f"  events дублікати:       {events_dups}")
print(f"  users дублікати:        {users_dups}")
print(f"  interactions дублікати: {interactions_dups}")

events       = events.drop_duplicates(subset=["event_id"])
users        = users.drop_duplicates(subset=["user_id"])
interactions = interactions.drop_duplicates(subset=["user_id", "event_id"])

# ── 3. Перевірка пропущених значень ───────────────────────────
print("\n Перевірка пропущених значень...")

print(f"  events NaN:       {events.isnull().sum().sum()}")
print(f"  users NaN:        {users.isnull().sum().sum()}")
print(f"  interactions NaN: {interactions.isnull().sum().sum()}")

# Спочатку видаляємо NaN
events       = events.dropna()
users        = users.dropna()
interactions = interactions.dropna()

# Потім парсимо теги (вже без NaN — безпечно)
print("\n Парсинг тегів і інтересів...")

events["tags"]     = events["tags"].apply(ast.literal_eval)
users["interests"] = users["interests"].apply(ast.literal_eval)

print("   tags і interests перетворені у списки")

# ── 4. Фільтрація холодного старту ────────────────────────────
print("\n  Фільтрація холодного старту (мін. 3 взаємодії)...")

MIN_INTERACTIONS = 3

before_users  = interactions["user_id"].nunique()
before_events = interactions["event_id"].nunique()

# Ітеративно фільтруємо поки не стабілізується
for iteration in range(10):
    # Юзери з мінімальною кількістю взаємодій
    user_counts  = interactions["user_id"].value_counts()
    valid_users  = user_counts[user_counts >= MIN_INTERACTIONS].index

    # Події з мінімальною кількістю взаємодій
    event_counts  = interactions["event_id"].value_counts()
    valid_events  = event_counts[event_counts >= MIN_INTERACTIONS].index

    filtered = interactions[
        interactions["user_id"].isin(valid_users) &
        interactions["event_id"].isin(valid_events)
    ]

    if len(filtered) == len(interactions):
        break
    interactions = filtered

after_users  = interactions["user_id"].nunique()
after_events = interactions["event_id"].nunique()

print(f"  Юзерів:  {before_users:,} → {after_users:,}")
print(f"  Подій:   {before_events:,} → {after_events:,}")
print(f"  Взаємодій після фільтрації: {len(interactions):,}")

# ── 5. Консистентність ─────────────────────────────────────────
print("\n Перевірка консистентності...")

valid_user_ids  = set(interactions["user_id"])
valid_event_ids = set(interactions["event_id"])

users  = users[users["user_id"].isin(valid_user_ids)]
events = events[events["event_id"].isin(valid_event_ids)]

print(f"  Фінально юзерів: {len(users):,}")
print(f"  Фінально подій:  {len(events):,}")

# ── 6. Перевірка типів даних ───────────────────────────────────
print("\n Перевірка типів даних...")

events["event_id"]        = events["event_id"].astype(int)
users["user_id"]          = users["user_id"].astype(int)
interactions["user_id"]   = interactions["user_id"].astype(int)
interactions["event_id"]  = interactions["event_id"].astype(int)
interactions["score"]     = interactions["score"].astype(float)

print("   Типи даних коректні")

# ── 7. Фінальна статистика ─────────────────────────────────────
n_users  = len(users)
n_events = len(events)
n_inter  = len(interactions)
density  = n_inter / (n_users * n_events) * 100

print("\n Фінальна статистика після препроцесингу:")
print(f"  Юзерів:      {n_users:,}")
print(f"  Подій:       {n_events:,}")
print(f"  Взаємодій:   {n_inter:,}")
print(f"  Density:     {density:.4f}%")
print(f"  Score mean:  {interactions['score'].mean():.4f}")

# ── 8. Збереження ──────────────────────────────────────────────
print("\n Збереження очищених файлів...")

events.to_csv(
    os.path.join(OUT_DIR, "events_clean.csv"), index=False, encoding='utf-8'
)
users.to_csv(
    os.path.join(OUT_DIR, "users_clean.csv"), index=False, encoding='utf-8'
)
interactions.to_csv(
    os.path.join(OUT_DIR, "interactions_clean.csv"), index=False, encoding='utf-8'
)

print(f"   events_clean.csv       → {len(events):,} подій")
print(f"   users_clean.csv        → {len(users):,} юзерів")
print(f"   interactions_clean.csv → {len(interactions):,} взаємодій")

print("\n" + "=" * 60)
print("   КРОК 2 ПОВНІСТЮ ЗАВЕРШЕНО")
print("  Запускай 3_build_features.py")
print("=" * 60)