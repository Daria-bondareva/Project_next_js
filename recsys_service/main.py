# recsys_service/main.py

from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv

# --- НАЛАШТУВАННЯ ---
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client.get_database()

users_collection = db["users"]
events_collection = db["events"]

CF_WEIGHT = 5
CB_WEIGHT = 10
CONTEXT_PENALTY = 10 
CONTEXT_BONUS = 5

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Hybrid AI Service is running"}

# --- ДОПОМІЖНІ ФУНКЦІЇ ---

def calculate_cb_score_normalized(event_tags, user_interests):
    if not event_tags or not user_interests:
        return 0
    event_set = set(event_tags)
    user_set = set(user_interests)
    intersection = event_set.intersection(user_set)
    return (len(intersection) / max(len(event_set), 1)) * CB_WEIGHT

def apply_context_penalty(score, event_tags, current_hour):
    is_morning = 5 <= current_hour < 12
    is_evening = 18 <= current_hour <= 23
    
    modifier = 0
    
    if is_morning and 'ВЕЧІР' in event_tags: modifier -= CONTEXT_PENALTY
    if is_evening and 'РАНОК' in event_tags: modifier -= CONTEXT_PENALTY
    
    if is_morning and 'РАНОК' in event_tags: modifier += CONTEXT_BONUS
    if is_evening and 'ВЕЧІР' in event_tags: modifier += CONTEXT_BONUS
    
    return score + modifier

# --- ГОЛОВНИЙ ЕНДПОІНТ ---

@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: str):
    # 1. ЗАВАНТАЖЕННЯ ДАНИХ КОРИСТУВАЧА
    try:
        target_user = users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid User ID")
        
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user_interests = target_user.get("interests", [])

    # 2. ЗАВАНТАЖЕННЯ ПОДІЙ
    events_cursor = events_collection.find()
    events_list = list(events_cursor)
    
    if not events_list:
        return []
    
    events_df = pd.DataFrame(events_list)
    
    # 🛠 FIX #1: ПРАВИЛЬНА ТИПІЗАЦІЯ STRING
    events_df['_id'] = events_df['_id'].astype(str)
    
    # Обробка тегів
    if 'tags' not in events_df.columns: 
        events_df['tags'] = [[] for _ in range(len(events_df))]
    else: 
        events_df['tags'] = events_df['tags'].apply(lambda x: x if isinstance(x, list) else [])

    # Обробка учасників: КОНВЕРТУЄМО КОЖЕН ID В STR
    if 'participants' not in events_df.columns: 
        events_df['participants'] = [[] for _ in range(len(events_df))]
    else: 
        events_df['participants'] = events_df['participants'].apply(
            lambda x: [str(p) for p in x] if isinstance(x, list) else []
        )

    # Обробка автора: КОНВЕРТУЄМО В STR
    if 'userId' in events_df.columns: 
        events_df['userId'] = events_df['userId'].astype(str) # Це важливо для фільтрації!

    # ---------------------------------------------------------
    # ЕТАП 1: CONTENT-BASED
    # ---------------------------------------------------------
    events_df['cb_score'] = events_df['tags'].apply(
        lambda tags: calculate_cb_score_normalized(tags, user_interests)
    )

    # ---------------------------------------------------------
    # ЕТАП 2: COLLABORATIVE FILTERING
    # ---------------------------------------------------------
    events_df['cf_score'] = 0.0 
    
    try:
        all_users = list(users_collection.find({}, {"_id": 1}))
        all_user_ids = [str(u["_id"]) for u in all_users]
        all_event_ids = events_df['_id'].tolist()

        if len(all_user_ids) > 1 and user_id in all_user_ids:
            # Будуємо матрицю
            user_item_matrix = pd.DataFrame(0, index=all_user_ids, columns=all_event_ids)
            for _, event in events_df.iterrows():
                evt_id = event['_id']
                for p in event['participants']:
                    if p in all_user_ids:
                        user_item_matrix.loc[p, evt_id] = 1
            
            # 🛠 FIX #2: ЗАХИСТ ВІД НУЛЬОВОЇ МАТРИЦІ
            if user_item_matrix.sum().sum() > 0:
                user_vector = user_item_matrix.loc[user_id].values.reshape(1, -1)
                
                if user_vector.sum() > 0:
                    sim_scores = cosine_similarity(user_vector, user_item_matrix.values)[0]
                    sim_series = pd.Series(sim_scores, index=user_item_matrix.index)
                    
                    similar_users = sim_series.drop(user_id).sort_values(ascending=False).head(10)
                    
                    cf_scores = {}
                    for other_user, similarity in similar_users.items():
                        if similarity <= 0: continue
                        
                        other_history = user_item_matrix.loc[other_user]
                        attended_indices = other_history[other_history == 1].index
                        
                        for evt_id in attended_indices:
                            cf_scores[evt_id] = cf_scores.get(evt_id, 0) + (similarity * CF_WEIGHT)
                    
                    events_df['cf_score'] = events_df['_id'].map(cf_scores).fillna(0)
            
    except Exception as e:
        print(f"CF Skipped: {e}")

    # ---------------------------------------------------------
    # ЕТАП 3: ОБ'ЄДНАННЯ
    # ---------------------------------------------------------
    events_df['total_score'] = events_df['cb_score'] + events_df['cf_score']
    
    current_hour = datetime.now().hour
    events_df['final_score'] = events_df.apply(
        lambda row: apply_context_penalty(row['total_score'], row['tags'], current_hour), 
        axis=1
    )

    # 🛠 FIX #3: CLIP (Не даємо балам впасти нижче нуля)
    events_df['final_score'] = events_df['final_score'].clip(lower=0)

    # ---------------------------------------------------------
    # ЕТАП 4: ФІЛЬТРАЦІЯ
    # ---------------------------------------------------------
    
    # 1. Прибираємо власні події (Тепер працює, бо userId це string)
    events_df = events_df[events_df['userId'] != user_id]

    # 2. Прибираємо вже відвідані (Тепер працює, бо participants це list[string])
    events_df = events_df[~events_df['participants'].apply(lambda x: user_id in x)]
    
    # 3. Прибираємо минулі
    now = datetime.now()
    if 'date' in events_df.columns:
        events_df['date'] = pd.to_datetime(events_df['date'])
        events_df = events_df[events_df['date'] > now]

    # 4. Прибираємо нульові
    events_df = events_df[events_df['final_score'] > 0]

    recommendations = events_df.sort_values(by='final_score', ascending=False).head(5)

    return recommendations[['_id', 'title', 'date', 'tags', 'final_score']].to_dict(orient='records')