# =============================================================
# КРОК 1 — Підготовка даних
# =============================================================
# Що робить цей файл:
#   Бере два сирих датасети і будує три файли для навчання моделі.
#
# Вхідні дані (data/raw/):
#   - tags.dat              — Last.fm: ID тегу → назва жанру (rock, pop, metal...)
#   - user_artists.dat      — Last.fm: скільки разів юзер слухав артиста (вага)
#   - user_taggedartists.dat— Last.fm: які теги юзер ставив артистам
#   - event_dataset.csv     — події: Topic, Event Type, Location, Day of Week
#
# Що будує (data/processed/):
#   - events.csv       — події з тегами (МУЗИКА, ВЕЧІР, IT...)
#                        теги будуються з Topic + Event Type + Day of Week
#   - users.csv        — юзери з інтересами
#                        Last.fm жанри замінюються на наші теги через LASTFM_TAG_MAP
#   - interactions.csv — оцінки юзер → подія через Jaccard similarity тегів
#                        score = (спільні теги / всі теги) * середня вага прослуховувань
#
# Логіка підміни жанрів:
#   Last.fm жанр "rock"    → наш тег МУЗИКА
#   Last.fm жанр "chiptune"→ наш тег ІГРИ
#   Topic "Technology"     → наш тег IT
#   Day "Saturday"         → наш тег ОФЛАЙН
#   (повна таблиця: LASTFM_TAG_MAP, TOPIC_TAG_MAP, EVENT_TYPE_TAG_MAP, DAY_FORMAT_MAP)
# =============================================================

import pandas as pd
import numpy as np
import os
from collections import Counter

# ── Шляхи ──────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
OUT_DIR  = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(OUT_DIR, exist_ok=True)

print("=" * 60)
print("  КРОК 1 — Підготовка даних")
print("  Джерела: Last.fm HetRec 2011 + Event Dataset")
print("=" * 60)

# ── Маппинг Last.fm тегів → твої теги (тільки чисті збіги) ────
LASTFM_TAG_MAP = {
    # МУЗИКА
    'metal': 'МУЗИКА', 'alternative metal': 'МУЗИКА',
    'black metal': 'МУЗИКА', 'death metal': 'МУЗИКА',
    'gothic metal': 'МУЗИКА', 'heavy metal': 'МУЗИКА',
    'rock': 'МУЗИКА', 'hard rock': 'МУЗИКА',
    'classic rock': 'МУЗИКА', 'indie rock': 'МУЗИКА',
    'alternative rock': 'МУЗИКА', 'psychedelic rock': 'МУЗИКА',
    'progressive rock': 'МУЗИКА', 'punk rock': 'МУЗИКА',
    'post-rock': 'МУЗИКА', 'grunge': 'МУЗИКА',
    'pop': 'МУЗИКА', 'synth pop': 'МУЗИКА',
    'synth-pop': 'МУЗИКА', 'synthpop': 'МУЗИКА',
    'electropop': 'МУЗИКА', 'indie pop': 'МУЗИКА',
    'dance pop': 'МУЗИКА', 'teen pop': 'МУЗИКА',
    'electronic': 'МУЗИКА', 'electronica': 'МУЗИКА',
    'electro': 'МУЗИКА', 'techno': 'МУЗИКА',
    'trance': 'МУЗИКА', 'progressive trance': 'МУЗИКА',
    'house': 'МУЗИКА', 'club house': 'МУЗИКА',
    'dubstep': 'МУЗИКА', 'drum and bass': 'МУЗИКА',
    'idm': 'МУЗИКА', 'ambient': 'МУЗИКА',
    'downtempo': 'МУЗИКА', 'trip-hop': 'МУЗИКА',
    'trip hop': 'МУЗИКА', 'chillout': 'МУЗИКА',
    'chill out': 'МУЗИКА', 'hip-hop': 'МУЗИКА',
    'hip hop': 'МУЗИКА', 'hiphop': 'МУЗИКА',
    'rap': 'МУЗИКА', 'rnb': 'МУЗИКА',
    'r and b': 'МУЗИКА', 'soul': 'МУЗИКА',
    'funk': 'МУЗИКА', 'disco': 'МУЗИКА',
    'jazz': 'МУЗИКА', 'acid jazz': 'МУЗИКА',
    'blues': 'МУЗИКА', 'folk': 'МУЗИКА',
    'country': 'МУЗИКА', 'reggae': 'МУЗИКА',
    'ska': 'МУЗИКА', 'swing': 'МУЗИКА',
    'classical': 'МУЗИКА', 'modern classical': 'МУЗИКА',
    'indie': 'МУЗИКА', 'alternative': 'МУЗИКА',
    'punk': 'МУЗИКА', 'post-punk': 'МУЗИКА',
    'new wave': 'МУЗИКА', 'gothic': 'МУЗИКА',
    'industrial': 'МУЗИКА', 'experimental': 'МУЗИКА',
    'acoustic': 'МУЗИКА', 'instrumental': 'МУЗИКА',
    'singer-songwriter': 'МУЗИКА', 'shoegaze': 'МУЗИКА',
    'dream pop': 'МУЗИКА', 'britpop': 'МУЗИКА',
    'dance': 'МУЗИКА', 'groove': 'МУЗИКА',

    # КІНО — тільки реально про кіно
    'soundtrack': 'КІНО', 'film score': 'КІНО',
    'anime': 'КІНО', 'movie music': 'КІНО',
    'horror film music': 'КІНО', 'game ost': 'КІНО',

    # ІГРИ — тільки реально про ігри
    'chiptune': 'ІГРИ', 'game': 'ІГРИ',
    'game music': 'ІГРИ', 'game soundtracks': 'ІГРИ',
    'nintendo': 'ІГРИ', 'nintendo-core': 'ІГРИ',
    'video game music': 'ІГРИ', 'video game': 'ІГРИ',
    '8-bit': 'ІГРИ', 'videogame': 'ІГРИ',

    # РАНОК — спокійні, розслаблені жанри
    'lounge': 'РАНОК', 'new age': 'РАНОК',
    'cafe del mar': 'РАНОК', 'peaceful': 'РАНОК',
    'relaxing': 'РАНОК', 'meditation': 'РАНОК',
    'calm': 'РАНОК', 'morning': 'РАНОК',
    'ambient lounge': 'РАНОК', 'sleep music': 'РАНОК',

    # ВЕЧІР — енергійні, клубні
    'party': 'ВЕЧІР', 'rave': 'ВЕЧІР',
    'club': 'ВЕЧІР', 'hi-nrg': 'ВЕЧІР',
    'night': 'ВЕЧІР', 'party time': 'ВЕЧІР',

    # ПОДОРОЖІ — world music, етніка
    'world music': 'ПОДОРОЖІ', 'world': 'ПОДОРОЖІ',
    'ethnic': 'ПОДОРОЖІ', 'latin': 'ПОДОРОЖІ',
    'celtic': 'ПОДОРОЖІ', 'latin pop': 'ПОДОРОЖІ',
    'bossa nova': 'ПОДОРОЖІ', 'flamenco': 'ПОДОРОЖІ',
    'afrobeat': 'ПОДОРОЖІ', 'samba': 'ПОДОРОЖІ',
    'zouk': 'ПОДОРОЖІ', 'kizomba': 'ПОДОРОЖІ',
    'reggaeton': 'ПОДОРОЖІ', 'cumbia': 'ПОДОРОЖІ',
}

# ── Маппинг event_dataset Topic → твої теги ────────────────────
TOPIC_TAG_MAP = {
    'Music':      ['МУЗИКА', 'РАНОК'],        # музичні події → також ранкові
    'Technology': ['IT'],
    'Art':        ['МИСТЕЦТВО', 'КІНО'],      # арт події → також кіно
    'Business':   ['БІЗНЕС'],
    'Education':  ['ЛЕКЦІЯ'],
    'Fun':        ['ІГРИ', 'ВЕЧІР'],          # розваги → також вечір
    'Politics':   ['БІЗНЕС'],
}

# ── Маппинг Event Type → додаткові теги ────────────────────────
EVENT_TYPE_TAG_MAP = {
    'Concert':         ['МУЗИКА', 'ВЕЧІР'],
    'Conference':      ['БІЗНЕС', 'ЛЕКЦІЯ'],
    'Workshop':        ['ЛЕКЦІЯ', 'МИСТЕЦТВО'],
    'Seminar':         ['ЛЕКЦІЯ', 'НАУКА'],
    'Birthday':        ['ВЕЧІР', 'РАНОК'],
    'Christmas Eve':   ['ВЕЧІР', 'ПОДОРОЖІ'],  # свято → подорожі/культура
    'Valedictory':     ['ЛЕКЦІЯ'],
    'Naming_Ceremony': ['ВЕЧІР'],
}

# ── Маппинг Day of Week → ОНЛАЙН/ОФЛАЙН ───────────────────────
DAY_FORMAT_MAP = {
    'Monday':    'ОНЛАЙН',
    'Tuesday':   'ОНЛАЙН',
    'Wednesday': 'ОНЛАЙН',
    'Thursday':  'ОНЛАЙН',
    'Friday':    'ВЕЧІР',
    'Saturday':  'ОФЛАЙН',
    'Sunday':    'ОФЛАЙН',
}

# ── Завантаження Last.fm файлів ────────────────────────────────
print("\n Завантаження Last.fm файлів...")

tags_df = pd.read_csv(
    os.path.join(RAW_DIR, "tags.dat"),
    sep="\t", encoding="latin-1"
)
user_artists = pd.read_csv(
    os.path.join(RAW_DIR, "user_artists.dat"),
    sep="\t", encoding="latin-1"
)
user_tagged = pd.read_csv(
    os.path.join(RAW_DIR, "user_taggedartists.dat"),
    sep="\t", encoding="latin-1"
)

print(f"  tags:               {len(tags_df):>7,} рядків")
print(f"  user_artists:       {len(user_artists):>7,} рядків")
print(f"  user_taggedartists: {len(user_tagged):>7,} рядків")

# ── Завантаження event_dataset ─────────────────────────────────
print("\n Завантаження event_dataset.csv...")

events_raw = pd.read_csv(
    os.path.join(RAW_DIR, "event_dataset.csv"),
    encoding="utf-8"
)

print(f"  event_dataset:      {len(events_raw):>7,} рядків")
print(f"  колонки: {list(events_raw.columns)}")


# ── Частина 4: Побудова events.csv ────────────────────────────
print("\n Побудова events.csv...")

# Беремо 10,000 рядків — достатньо для навчання
events_raw = events_raw.sample(n=10000, random_state=42).reset_index(drop=True)

def build_event_tags(row):
    tags = set()
    
    # 1. З Topic
    topic_tags = TOPIC_TAG_MAP.get(row['Topic'], [])
    tags.update(topic_tags)
    
    # 2. З Event Type
    type_tags = EVENT_TYPE_TAG_MAP.get(row['Event Type'], [])
    tags.update(type_tags)
    
    # 3. З Day of Week → ОНЛАЙН/ОФЛАЙН/ВЕЧІР
    day_tag = DAY_FORMAT_MAP.get(row['Day of Week'], None)
    if day_tag:
        tags.add(day_tag)
    
    return list(tags)

def build_event_title(row):
    return f"{row['Event Type']} ({row['Topic']}) in {row['Location']}"

events_df = pd.DataFrame({
    'event_id': range(len(events_raw)),
    'title':    events_raw.apply(build_event_title, axis=1),
    'tags':     events_raw.apply(build_event_tags, axis=1),
})

# Залишаємо тільки події з хоча б 1 тегом
events_df = events_df[events_df['tags'].apply(len) > 0].reset_index(drop=True)
events_df['event_id'] = events_df.index

print(f"  Подій збудовано: {len(events_df):,}")
print(f"  Приклад 1: {events_df.iloc[0]['title']}")
print(f"  Теги 1:    {events_df.iloc[0]['tags']}")
print(f"  Приклад 2: {events_df.iloc[1]['title']}")
print(f"  Теги 2:    {events_df.iloc[1]['tags']}")

# Розподіл тегів
all_tags = [tag for tags in events_df['tags'] for tag in tags]
print(f"\n  Розподіл тегів:")
for tag, count in Counter(all_tags).most_common():
    print(f"    {tag}: {count}")

# Зберігаємо events.csv
events_df.to_csv(os.path.join(OUT_DIR, "events.csv"), index=False)
print(f"\n   events.csv збережено → {len(events_df):,} подій")

# ── Частина 5: Побудова users.csv ─────────────────────────────
print("\n Побудова users.csv...")

# Для кожного юзера збираємо теги які він ставив артистам
# user_tagged: userID, artistID, tagID, day, month, year
# tags_df:     tagID, tagValue

# Приєднуємо назви тегів до user_tagged
user_tags_named = user_tagged.merge(tags_df, on="tagID", how="left")

# Маппимо Last.fm теги → наші теги через LASTFM_TAG_MAP
user_tags_named["our_tag"] = (
    user_tags_named["tagValue"]
    .str.lower()
    .str.strip()
    .map(LASTFM_TAG_MAP)
)

# Прибираємо рядки де маппинг не знайшов відповідності
user_tags_named = user_tags_named.dropna(subset=["our_tag"])

# Для кожного юзера — унікальні mapped теги
users_df = (
    user_tags_named
    .groupby("userID")["our_tag"]
    .apply(lambda x: list(x.unique()))
    .reset_index()
    .rename(columns={"userID": "user_id", "our_tag": "interests"})
)

# Залишаємо тільки юзерів з хоча б 1 тегом
users_df = users_df[
    users_df["interests"].apply(len) > 0
].reset_index(drop=True)

print(f"  Юзерів збудовано: {len(users_df):,}")
print(f"  Приклад 1: user {users_df.iloc[0]['user_id']} → "
      f"{users_df.iloc[0]['interests']}")
print(f"  Приклад 2: user {users_df.iloc[1]['user_id']} → "
      f"{users_df.iloc[1]['interests']}")

# Розподіл інтересів
all_interests = [t for interests in users_df["interests"] for t in interests]
print(f"\n  Розподіл інтересів юзерів:")
for tag, count in Counter(all_interests).most_common():
    print(f"    {tag}: {count}")

# Зберігаємо users.csv
users_df.to_csv(os.path.join(OUT_DIR, "users.csv"), index=False)
print(f"\n  users.csv збережено → {len(users_df):,} юзерів")

# ── Частина 6: Побудова interactions.csv ──────────────────────
print("\n Побудова interactions.csv...")

import numpy as np

# Використовуємо вже існуючі DataFrame з пам'яті
# (не читаємо з диску повторно)
events_clean = events_df.copy()
users_clean  = users_df.copy()

# tags і interests вже є списками — парсинг не потрібен

# Нормалізуємо weight → score [0, 1] через log
user_artists["log_weight"] = np.log1p(user_artists["weight"])  # type: ignore
max_log = user_artists["log_weight"].max()
user_artists["norm_weight"] = user_artists["log_weight"] / max_log

# Середній norm_weight для кожного юзера → dict для швидкого lookup
weight_dict = (
    user_artists
    .groupby("userID")["norm_weight"]
    .mean()
    .to_dict()
)

# Перетворюємо події на список для швидкого циклу
events_list = [
    (int(row["event_id"]), set(row["tags"]))
    for _, row in events_clean.iterrows()
]

# Будуємо взаємодії через Jaccard similarity
print("  Обчислення взаємодій...")

rows = []
for _, user_row in users_clean.iterrows():
    user_id   = int(user_row["user_id"])
    interests = set(user_row["interests"])
    avg_w     = weight_dict.get(user_id, 0.5)

    for event_id, event_tags in events_list:
        overlap = interests & event_tags
        if not overlap:
            continue

        # Jaccard similarity — стандартний академічний підхід
        tag_score   = len(overlap) / len(interests | event_tags)
        final_score = round(tag_score * avg_w, 4)

        if final_score >= 0.15:
            rows.append({
                "user_id":  user_id,
                "event_id": event_id,
                "score":    final_score
            })

interactions_df = pd.DataFrame(rows)

print(f"  Взаємодій збудовано: {len(interactions_df):,}")
print(f"  Унікальних юзерів:   {interactions_df['user_id'].nunique():,}")
print(f"  Унікальних подій:    {interactions_df['event_id'].nunique():,}")
print(f"  Score — min: {interactions_df['score'].min():.4f}, "
      f"max: {interactions_df['score'].max():.4f}, "
      f"mean: {interactions_df['score'].mean():.4f}")

# Density матриці
n_users  = users_clean["user_id"].nunique()
n_events = events_clean["event_id"].nunique()
density  = len(interactions_df) / (n_users * n_events) * 100
print(f"  Density матриці:     {density:.4f}%")

# Зберігаємо
interactions_df.to_csv(
    os.path.join(OUT_DIR, "interactions.csv"), index=False
)
print(f"\n   interactions.csv збережено → {len(interactions_df):,} взаємодій")

print("\n" + "=" * 60)
print("   КРОК 1 ПОВНІСТЮ ЗАВЕРШЕНО")
print("  Файли збережено в data/processed/:")
print("    - events.csv")
print("    - users.csv")
print("    - interactions.csv")
print("  Запускай 2_preprocess.py")
print("=" * 60)