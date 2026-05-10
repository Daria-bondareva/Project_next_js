# ml_classic_service/evaluate_classic.py

import pandas as pd
import numpy as np
import pickle
import re
from pymongo import MongoClient
from sklearn.metrics.pairwise import linear_kernel
import os
from dotenv import load_dotenv

# --- НАЛАШТУВАННЯ ---
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")
MODEL_PATH = 'models/recommendation_model.pkl'
TOP_K = 5

# --- ПІДКЛЮЧЕННЯ ---
client = MongoClient(MONGO_URI)
db = client.get_database()
users_collection = db["users"]
events_collection = db["events"]

# --- ПРЕПРОЦЕСИНГ (Копія з main_classic_real.py) ---
def clean_text(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r"[^a-zA-Zа-яА-ЯёЁґҐіІїЇєЄ0-9\s'’]", ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def evaluate_classic_model():
    print(f"--- ОЦІНКА КЛАСИЧНОЇ МОДЕЛІ (Transfer Learning) ---")
    
    # 1. Завантаження моделі (Векторизатора)
    if not os.path.exists(MODEL_PATH):
        print(f" Файл {MODEL_PATH} не знайдено.")
        return

    print(" Завантаження моделі...")
    with open(MODEL_PATH, 'rb') as f:
        model_data = pickle.load(f)
    vectorizer = model_data['vectorizer']
    
    # 2. Завантаження РЕАЛЬНИХ даних
    print(" Завантаження даних з БД...")
    events = list(events_collection.find())
    users = list(users_collection.find())
    
    if not events or not users:
        print(" Недостатньо даних.")
        return

    # Готуємо DataFrame подій (Target Items)
    df_events = pd.DataFrame(events)
    df_events['_id'] = df_events['_id'].astype(str)
    
    # Створюємо "Soup" для подій (щоб векторизувати їх)
    # Це те саме, що робить ваш сервер при старті
    if 'tags' not in df_events.columns: df_events['tags'] = [[] for _ in range(len(df_events))]
    if 'description' not in df_events.columns: df_events['description'] = [""] * len(df_events)
    if 'title' not in df_events.columns: df_events['title'] = [""] * len(df_events)
    if 'userId' not in df_events.columns: df_events['userId'] = [""] * len(df_events)

    def make_soup(row):
        tags = " ".join(row.get('tags', [])) if isinstance(row.get('tags'), list) else ""
        desc = str(row.get('description') or "")
        title = str(row.get('title') or "")
        return f"{title} {tags} {desc}"

    df_events['soup'] = df_events.apply(make_soup, axis=1)
    df_events['cleaned_text'] = df_events['soup'].apply(clean_text)
    
    # ВЕКТОРИЗАЦІЯ ПОДІЙ (Building Matrix)
    try:
        events_matrix = vectorizer.transform(df_events['cleaned_text'])
    except Exception as e:
        print(f" Помилка векторизації подій: {e}")
        return

    # 3. ЦИКЛ ОЦІНКИ (Leave-One-Out)
    hits = 0
    total_tests = 0
    
    print(f" Тестування на {len(users)} користувачах...")

    for user in users:
        user_id = str(user['_id'])
        interests = user.get('interests', [])
        
        # Якщо немає інтересів - ми не можемо нічого рекомендувати в цій моделі
        if not interests: continue

        # Знаходимо історію кліків юзера
        user_history = []
        for _, event in df_events.iterrows():
            if 'participants' in event and isinstance(event['participants'], list):
                # Конвертуємо participants в строки для пошуку
                participants_str = [str(p) for p in event['participants']]
                if user_id in participants_str:
                    user_history.append(event['_id'])
        
        # Тестуємо тільки тих, хто хоч кудись ходив (мінімум 1 подія)
        if len(user_history) < 1: continue

        # --- ТЕСТ ---
        # 1. Ховаємо останню подію (Ground Truth)
        hidden_event_id = user_history[-1]
        
        # 2. Векторизуємо інтереси юзера
        user_query = " ".join(interests)
        user_vector = vectorizer.transform([clean_text(user_query)])
        
        # 3. Рахуємо схожість з усіма подіями
        sim_scores = linear_kernel(user_vector, events_matrix).flatten()
        
        # 4. Ранжуємо
        df_events['score'] = sim_scores
        
        # Фільтруємо:
        # - Прибираємо власні події
        # - Прибираємо події, які юзер ВЖЕ бачив (крім прихованої!)
        visible_history = set(user_history[:-1])
        
        candidates = df_events[
            (df_events['userId'] != user_id) & 
            (~df_events['_id'].isin(visible_history))
        ]
        
        # Топ-K рекомендацій
        recommendations = candidates.sort_values('score', ascending=False).head(TOP_K)
        recommended_ids = recommendations['_id'].tolist()
        
        # 5. Перевірка
        if hidden_event_id in recommended_ids:
            hits += 1
        
        total_tests += 1

    # 4. РЕЗУЛЬТАТ
    if total_tests > 0:
        precision = hits / total_tests
        print(f"\n--- РЕЗУЛЬТАТИ (Classic Model) ---")
        print(f"Тестів: {total_tests}")
        print(f"Влучань: {hits}")
        print(f"Precision@{TOP_K}: {precision:.4f} ({precision*100:.2f}%)")
    else:
        print("Недостатньо активних користувачів для тесту.")

if __name__ == "__main__":
    evaluate_classic_model()