# recsys_service/evaluate.py

from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from datetime import datetime
from dotenv import load_dotenv

# --- НАЛАШТУВАННЯ ---
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client.get_database()

# ❗ Пункт 6: Виносимо "магічні числа" в константи
CF_WEIGHT = 20
CB_WEIGHT = 10
TOP_K = 5

def calculate_cb_score_normalized(event_tags, user_interests):
    """
    ❗ Пункт 4: Нормований Content-Based скоринг.
    Бали залежать від % збігу, а не просто від кількості.
    """
    if not event_tags or not user_interests:
        return 0
    
    event_set = set(event_tags)
    user_set = set(user_interests)
    intersection = event_set.intersection(user_set)
    
    # Формула: (Збіги / Довжина тегів події) * Вага
    # max(..., 1) захищає від ділення на нуль
    return (len(intersection) / max(len(event_set), 1)) * CB_WEIGHT

def evaluate_optimized():
    print(f"--- ПОЧАТОК ОЦІНКИ (Optimized Precision@{TOP_K}) ---")
    
    # 1. ЗАВАНТАЖЕННЯ ДАНИХ (Один раз)
    events = list(db.events.find())
    users = list(db.users.find())
    
    if not events or not users:
        print("Недостатньо даних.")
        return

    # Препроцесинг подій
    events_df = pd.DataFrame(events)
    events_df['_id'] = events_df['_id'].astype(str)
    
    # ❗ Пункт 8: Фільтруємо події, які вже минули (Business Logic)
    # Закоментуйте цей рядок, якщо у вас всі тестові події в минулому!
    # events_df = events_df[events_df['date'] > datetime.now()] 

    if 'participants' not in events_df.columns:
        events_df['participants'] = [[] for _ in range(len(events_df))]
    else:
        events_df['participants'] = events_df['participants'].apply(
            lambda x: [str(p) for p in x] if isinstance(x, list) else []
        )

    if 'tags' not in events_df.columns:
        events_df['tags'] = [[] for _ in range(len(events_df))]
    else:
        events_df['tags'] = events_df['tags'].apply(lambda x: x if isinstance(x, list) else [])

    if 'userId' in events_df.columns:
        events_df['userId'] = events_df['userId'].astype(str)

    # 2. ПІДГОТОВКА МАТРИЦІ (❗ Пункт 1 та 3: Робимо це ДО циклу)
    print("📊 Побудова матриці взаємодій...")
    all_user_ids = [str(u['_id']) for u in users]
    all_event_ids = events_df['_id'].tolist()
    
    # Створюємо DF, заповнений нулями
    user_item_matrix = pd.DataFrame(0, index=all_user_ids, columns=all_event_ids)

    # Заповнюємо матрицю
    for _, event in events_df.iterrows():
        evt_id = event['_id']
        for p in event['participants']:
            if p in all_user_ids:
                user_item_matrix.loc[p, evt_id] = 1

    # Рахуємо схожість ВСІХ з усіма одразу
    # Це найважча операція, і ми робимо її 1 раз замість N разів
    cosine_sim_matrix = cosine_similarity(user_item_matrix)
    similarity_df = pd.DataFrame(cosine_sim_matrix, index=all_user_ids, columns=all_user_ids)

    # 3. ПІДГОТОВКА ТЕСТОВИХ ЮЗЕРІВ
    active_users = []
    for user in users:
        user_id = str(user['_id'])
        # Знаходимо історію цього юзера з матриці (швидше, ніж бігати по списку)
        user_vector = user_item_matrix.loc[user_id]
        history = user_vector[user_vector == 1].index.tolist()
        
        if len(history) >= 2:
            active_users.append({
                'id': user_id,
                'history': history,
                'interests': user.get('interests', [])
            })

    print(f"Кількість користувачів для тесту: {len(active_users)}")
    
    hits = 0
    total_tests = 0

    # 4. ЦИКЛ ОЦІНКИ (Швидкий)
    for user_data in active_users:
        user_id = user_data['id']
        full_history = user_data['history'] # Це список ID подій
        user_interests = user_data['interests']

        # Leave-One-Out (Беремо останню за часом або списком)
        # ❗ Пункт 5: Можна взяти random.choice(full_history), але last теж ок
        hidden_event_id = full_history[-1] 
        visible_history = set(full_history[:-1]) # Використовуємо set для швидкого пошуку

        # --- A. COLLABORATIVE FILTERING (Швидкий look-up) ---
        cf_scores = {}
        
        # Беремо вже пораховані схожості для цього юзера
        similar_users = similarity_df[user_id].sort_values(ascending=False).drop(user_id)
        top_k_users = similar_users.head(10) # ❗ Пункт 2 (порада): Можна взяти топ-10

        for other_user, similarity in top_k_users.items():
            if similarity <= 0: continue
            
            # Дивимось, де був цей "сусід"
            other_history = user_item_matrix.loc[other_user]
            # Беремо події, де сусід був (1), а ми ще ні (або це прихована подія)
            # Важливо: ми "забуваємо", що ми були на hidden_event_id для чистоти експерименту
            attended_indices = other_history[other_history == 1].index
            
            for evt_id in attended_indices:
                if evt_id not in visible_history:
                    # Нараховуємо бали
                    cf_scores[evt_id] = cf_scores.get(evt_id, 0) + (similarity * CF_WEIGHT)

        # --- B. CONTENT-BASED & HYBRID ---
        final_scores = {}

        for _, event in events_df.iterrows():
            evt_id = event['_id']
            
            # Фільтри
            if evt_id in visible_history: continue
            
            # ❗ Пункт 7: Не рекомендувати власні події
            if str(event.get('userId')) == user_id: continue

            # CB Score (Нормований)
            cb_score = calculate_cb_score_normalized(event['tags'], user_interests)
            
            # CF Score
            cf_score = cf_scores.get(evt_id, 0)
            
            final_scores[evt_id] = cb_score + cf_score

        # Сортування
        recommended = sorted(final_scores, key=final_scores.get, reverse=True)[:TOP_K]

        # Перевірка
        if hidden_event_id in recommended:
            hits += 1
        
        total_tests += 1

    # 5. РЕЗУЛЬТАТ
    if total_tests > 0:
        precision = hits / total_tests
        print(f"\n--- РЕЗУЛЬТАТИ (Оптимізовані) ---")
        print(f"Тестів: {total_tests}")
        print(f"Влучань: {hits}")
        print(f"Precision@{TOP_K}: {precision:.4f} ({precision*100:.2f}%)")
    else:
        print("Мало даних.")

if __name__ == "__main__":
    evaluate_optimized()