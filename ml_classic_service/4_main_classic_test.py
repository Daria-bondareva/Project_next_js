#============================================================
# 1: Імпорт та налаштування
#============================================================
from fastapi import FastAPI, HTTPException
import pickle
import pandas as pd
import numpy as np
from pymongo import MongoClient
from bson.objectid import ObjectId
from sklearn.metrics.pairwise import linear_kernel
import os
from dotenv import load_dotenv
import re
import uvicorn

# Налаштування
load_dotenv()
MODEL_PATH = 'models/recommendation_model.pkl'
MONGO_URI = os.getenv("MONGODB_URI")

# Ініціалізація FastAPI
app = FastAPI(title="Classic ML Recommender")

#============================================================
# 2: Підключення до бази даних
#============================================================
def get_database():
    """Підключення до MongoDB для отримання живих даних користувачів."""
    try:
        client = MongoClient(MONGO_URI)
        db = client.get_database()
        return db
    except Exception as e:
        print(f" Помилка підключення до БД: {e}")
        return None

db = get_database()
users_collection = db["users"] if db is not None else None

#============================================================
# 3: Завантаження моделі
#============================================================
def load_model(filepath):
    """
    Завантажує навчену модель та її компоненти з файлу.
    """
    print(f" Завантаження моделі з {filepath}...")
    try:
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        print(" Модель успішно завантажена!")
        print(f"   -> Подій у пам'яті: {len(model_data['events_df'])}")
        return model_data
    except FileNotFoundError:
        print(f"❌ ПОМИЛКА: Файл {filepath} не знайдено. Запустіть train_model.py")
        return None
    except Exception as e:
        print(f"❌ Критична помилка при завантаженні моделі: {e}")
        return None


# Завантажуємо модель глобально при старті
MODEL_DATA = None
MODEL_DATA = load_model(MODEL_PATH)

#============================================================
# 4: Допоміжні функції (Препроцесинг)
#============================================================
def clean_text(text):
    """
    Очищає текст так само, як це робилося при навчанні.
    """
    if not isinstance(text, str): return ""
    text = text.lower()
    # Видалення спецсимволів (зберігаючи кирилицю та цифри)
    text = re.sub(r"[^a-zA-Zа-яА-ЯёЁґҐіІїЇєЄ0-9\s'’]", ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

#============================================================
# 5: Логіка рекомендацій
#============================================================
def calculate_recommendations(user_vector, tfidf_matrix, df, top_n=5):
    """
    Рахує схожість і повертає топ подій.
    """
    # Рахуємо косинусну схожість (User Vector vs All Events Matrix)
    # Результат - масив чисел [0.1, 0.5, 0.0, ...] для кожної події
    sim_scores = linear_kernel(user_vector, tfidf_matrix).flatten()
    
    # Створюємо тимчасовий DF для сортування
    results = df.copy()
    results['score'] = sim_scores
    
    # Фільтруємо (беремо тільки ті, що мають хоч якусь схожість)
    # та сортуємо від найбільшого до найменшого
    candidates = results[results['score'] > 0].sort_values('score', ascending=False).head(50)
    
    # 4. РОЗУМНА ФІЛЬТРАЦІЯ (Дедуплікація)
    unique_recommendations = []
    seen_descriptions = set()
    
    for _, row in candidates.iterrows():
        # Беремо перші 30 символів опису як "відбиток" (щоб не показувати однакові)
        desc_signature = row['description'][:30]
        
        if desc_signature not in seen_descriptions:
            unique_recommendations.append(row)
            seen_descriptions.add(desc_signature)
        
        # Якщо назбирали достатньо - виходимо
        if len(unique_recommendations) >= top_n:
            break

    # Перетворюємо назад у DataFrame
    return pd.DataFrame(unique_recommendations)

#============================================================
# 6: API Ендпоінти
#============================================================
@app.get("/")
def read_root():
    status = "Active" if MODEL_DATA else "Model Error"
    return {"status": f"Classic ML Service: {status}"}

@app.get("/recommendations/{user_id}")
def recommend(user_id: str):
    """
    Головний ендпоінт для отримання рекомендацій.
    """
    # 1. ЛОГУВАННЯ 
    print(f" Request for recommendations | user_id={user_id}")

    # Перевірка стану сервісу
    if not MODEL_DATA:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    vectorizer = MODEL_DATA['vectorizer']
    tfidf_matrix = MODEL_DATA['tfidf_matrix']
    events_df = MODEL_DATA['events_df'].reset_index(drop=True)

    # 2. ОТРИМАННЯ ЮЗЕРА
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid User ID")
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 3. ОБРОБКА ІНТЕРЕСІВ 
    interests = user.get("interests", [])
    
    if isinstance(interests, str):
        # Якщо в базі чомусь записано рядок "IT", робимо список ["IT"]
        interests = [interests]
        
    if not interests:
        print("   -> У користувача немає інтересів.")
        return []

    # Формуємо запит
    user_query = " ".join(interests)
    user_query_cleaned = clean_text(user_query)
    
    # 4. ВЕКТОРИЗАЦІЯ
    try:
        user_vector = vectorizer.transform([user_query_cleaned])
    except Exception as e:
        print(f" Vectorization error: {e}")
        return []

    # 5. ЗАХИСТ ВІД ПУСТОГО ВЕКТОРА (Fix #3)
    # Якщо юзер ввів слова, яких немає в словнику моделі (наприклад "абракадабра")
    if user_vector.nnz == 0:
        print(" User vector is empty (no known words in interests).")
        return []

    # 6. РОЗРАХУНОК (Викликаємо нашу функцію!)
    # Тепер логіка ізольована і код чистий
    recs_df = calculate_recommendations(user_vector, tfidf_matrix, events_df)
    
    print(f" Found {len(recs_df)} recommendations.")
    
    cols_to_return = ['category', 'description']
    
    if 'score' in recs_df.columns:
        cols_to_return.append('score')

    if 'cleaned_text' in recs_df.columns:
        cols_to_return.append('cleaned_text')

    return recs_df[cols_to_return].to_dict(orient='records')

if __name__ == "__main__":
    uvicorn.run("main_classic:app", host="127.0.0.1", port=8001, reload=True)