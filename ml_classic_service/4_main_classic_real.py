# ml_classic_service/main_classic_real.py

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

# --- НАЛАШТУВАННЯ ---
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")
MODEL_PATH = 'models/recommendation_model.pkl' # Тут лежить навчений Vectorizer

app = FastAPI(title="Real Events ML Recommender")

# --- БАЗА ДАНИХ ---
client = MongoClient(MONGO_URI)
db = client.get_database()
users_collection = db["users"]
events_collection = db["events"]

# --- ГЛОБАЛЬНІ ЗМІННІ ---
# Ми будемо зберігати тут оброблені реальні події
REAL_EVENTS_DF = None
REAL_EVENTS_MATRIX = None
VECTORIZER = None

def clean_text(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r"[^a-zA-Zа-яА-ЯёЁґҐіІїЇєЄ0-9\s'’]", ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

# --- ЗАВАНТАЖЕННЯ ТА ПІДГОТОВКА ---

@app.on_event("startup")
def startup_event():
    global VECTORIZER, REAL_EVENTS_DF, REAL_EVENTS_MATRIX
    
    print(" 1. Завантаження 'мозку' (Kaggle Model)...")
    try:
        with open(MODEL_PATH, 'rb') as f:
            model_data = pickle.load(f)
        # Нам потрібен ТІЛЬКИ векторизатор (словник), матриця Kaggle нам не треба
        VECTORIZER = model_data['vectorizer']
        print(" Векторизатор завантажено!")
    except Exception as e:
        print(f" Критична помилка: {e}")
        return

    print(" 2. Завантаження РЕАЛЬНИХ подій з MongoDB...")
    events = list(events_collection.find())
    if not events:
        print(" У базі немає подій!")
        return

    # Створюємо DataFrame з реальних подій
    df = pd.DataFrame(events)
    df['_id'] = df['_id'].astype(str)
    
    # Готуємо текст (так само, як для Kaggle)
    # Об'єднуємо заголовок + теги + опис
    if 'tags' not in df.columns: df['tags'] = [[] for _ in range(len(df))]
    if 'description' not in df.columns: df['description'] = [""] * len(df)
    if 'title' not in df.columns: df['title'] = [""] * len(df)
    if 'userId' not in df.columns: df['userId'] = [""] * len(df)

    def make_soup(row):
        tags = " ".join(row.get('tags', [])) if isinstance(row.get('tags'), list) else ""
        desc = row.get('description') or ""  
        title = row.get('title') or ""
        return f"{title} {tags} {desc}"

    df['soup'] = df.apply(make_soup, axis=1)
    df['cleaned_text'] = df['soup'].apply(clean_text)
    
    print(f" Завантажено {len(df)} реальних подій.")

    print(" 3. Трансформація реальних подій у вектори...")
    try:
        # Використовуємо "Kaggle-знання" для наших подій
        REAL_EVENTS_MATRIX = VECTORIZER.transform(df['cleaned_text'])
        REAL_EVENTS_DF = df
        print(f" Матриця готова: {REAL_EVENTS_MATRIX.shape}")
    except Exception as e:
        print(f" Помилка векторизації: {e}")

@app.get("/")
def read_root():
    status = "Active" if REAL_EVENTS_MATRIX is not None else "Not Ready"
    return {"status": f"Real Data ML Service: {status}"}

@app.get("/recommendations/{user_id}")
def recommend(user_id: str):
    if REAL_EVENTS_MATRIX is None or VECTORIZER is None:
        raise HTTPException(status_code=500, detail="Service not initialized")

    # 1. Отримуємо юзера
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        return []
    
    if not user: return []
    
    interests = user.get("interests", [])
    if not interests: return []

    # 2. Векторизуємо інтереси юзера
    user_query = " ".join(interests)
    user_query_cleaned = clean_text(user_query)
    
    try:
        user_vector = VECTORIZER.transform([user_query_cleaned])
    except:
        return []

    # Захист: якщо інтереси юзера складаються зі слів, яких модель не знає
    if user_vector.nnz == 0:
        print(" Інтереси користувача невідомі цій моделі.")
        return []

    # 3. Рахуємо схожість (User vs Real Events)
    sim_scores = linear_kernel(user_vector, REAL_EVENTS_MATRIX).flatten()
    
    # 4. Формуємо відповідь
    results = REAL_EVENTS_DF.copy()
    results['score'] = sim_scores
    
    # Фільтруємо (не показуємо свої події)
    if 'userId' in results.columns:
        results = results[results['userId'].astype(str) != user_id]
    
    # Сортуємо
    recs = results[results['score'] > 0].sort_values('score', ascending=False).head(5)
    
    # Безпечний вибір колонок для відповіді
    cols = ['_id', 'title','date', 'description', 'tags', 'score']
    final_cols = [c for c in cols if c in recs.columns]
    
    recs = recs.fillna("")

    return recs[final_cols].to_dict(orient='records')

if __name__ == "__main__":
    # Запускаємо на порту 8002, щоб не заважати іншим
    uvicorn.run("main_classic_real:app", host="127.0.0.1", port=8002, reload=True)