# recsys_service/experiment_weights.py

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv

# Налаштування
load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database()

# Константи
CB_WEIGHT = 10
TOP_K = 5
WEIGHTS_TO_TEST = [0, 5, 10, 15, 20, 25, 30, 35, 40, 50]

def calculate_cb_score(event_tags, user_interests):
    if not event_tags or not user_interests: return 0
    intersection = set(event_tags).intersection(set(user_interests))
    return (len(intersection) / max(len(event_tags), 1)) * CB_WEIGHT

def run_experiment():
    print("🚀 ПОЧАТОК ЕКСПЕРИМЕНТУ (Hardcore Mode)...")

    # --- 1. ПІДГОТОВКА ДАНИХ (Один раз для всіх тестів) ---
    print("⏳ Завантаження даних та побудова матриць...")
    
    events = list(db.events.find())
    users = list(db.users.find())
    
    events_df = pd.DataFrame(events)
    events_df['_id'] = events_df['_id'].astype(str)
    # Заповнюємо пропуски
    if 'tags' not in events_df.columns: events_df['tags'] = [[] for _ in range(len(events_df))]
    else: events_df['tags'] = events_df['tags'].apply(lambda x: x if isinstance(x, list) else [])
    
    if 'participants' not in events_df.columns: events_df['participants'] = [[] for _ in range(len(events_df))]
    else: events_df['participants'] = events_df['participants'].apply(lambda x: [str(p) for p in x] if isinstance(x, list) else [])

    all_user_ids = [str(u['_id']) for u in users]
    all_event_ids = events_df['_id'].tolist()

    # Будуємо матрицю взаємодій
    user_item_matrix = pd.DataFrame(0, index=all_user_ids, columns=all_event_ids)
    for _, event in events_df.iterrows():
        evt_id = event['_id']
        for p in event['participants']:
            if p in all_user_ids:
                user_item_matrix.loc[p, evt_id] = 1

    # Рахуємо схожість юзерів (Це найважча операція, робимо 1 раз)
    cosine_sim_matrix = cosine_similarity(user_item_matrix)
    similarity_df = pd.DataFrame(cosine_sim_matrix, index=all_user_ids, columns=all_user_ids)

    # Підготовка тестових юзерів (Leave-One-Out)
    test_cases = []
    for user in users:
        uid = str(user['_id'])
        # Реальна історія з матриці
        history_indices = user_item_matrix.loc[uid][user_item_matrix.loc[uid] == 1].index.tolist()
        
        if len(history_indices) < 2: continue
        
        hidden_event = history_indices[-1]
        visible_history = set(history_indices[:-1])
        
        test_cases.append({
            'user_id': uid,
            'interests': user.get('interests', []),
            'hidden': hidden_event,
            'visible': visible_history
        })

    print(f"✅ Дані готові. Тестових випадків: {len(test_cases)}")
    
    # --- 2. ЦИКЛ ЕКСПЕРИМЕНТУ ---
    results_precision = []

    for cf_weight in WEIGHTS_TO_TEST:
        print(f"\n🧪 Тестуємо вагу CF = {cf_weight} ...", end="")
        hits = 0
        
        for case in test_cases:
            user_id = case['user_id']
            visible_hist = case['visible']
            
            # --- A. CF Score (з поточною вагою) ---
            cf_scores = {}
            # Знаходимо сусідів (з уже готової матриці!)
            similar_users = similarity_df[user_id].sort_values(ascending=False).drop(user_id).head(10)
            
            for other_user, similarity in similar_users.items():
                if similarity <= 0: continue
                # Історія сусіда
                other_hist = user_item_matrix.loc[other_user]
                attended = other_hist[other_hist == 1].index
                
                for evt_id in attended:
                    if evt_id not in visible_hist:
                        # ОСЬ ВОНО: Використовуємо змінну вагу
                        cf_scores[evt_id] = cf_scores.get(evt_id, 0) + (similarity * cf_weight)

            # --- B. Combine with CB ---
            final_scores = {}
            for _, event in events_df.iterrows():
                evt_id = event['_id']
                if evt_id in visible_hist: continue
                if str(event.get('userId')) == user_id: continue

                cb = calculate_cb_score(event['tags'], case['interests'])
                cf = cf_scores.get(evt_id, 0)
                
                final_scores[evt_id] = cb + cf
            
            # Топ-5
            recs = sorted(final_scores, key=final_scores.get, reverse=True)[:TOP_K]
            
            if case['hidden'] in recs:
                hits += 1
        
        precision = hits / len(test_cases)
        results_precision.append(precision)
        print(f" -> Precision: {precision:.4f}")

    # --- 3. ВІЗУАЛІЗАЦІЯ ---
    print("\n📊 Побудова графіка...")
    
    plt.figure(figsize=(10, 6))
    plt.plot(WEIGHTS_TO_TEST, results_precision, marker='o', linestyle='-', color='#4ECDC4', linewidth=2, markersize=8)
    
    # Знаходимо найкращу точку
    max_prec = max(results_precision)
    best_weight = WEIGHTS_TO_TEST[results_precision.index(max_prec)]
    
    plt.plot(best_weight, max_prec, marker='o', markersize=12, markerfacecolor='red', 
             label=f'Оптимум (CF={best_weight}, P={max_prec:.2f})')

    plt.title(f"Експериментальна залежність Precision@{TOP_K} від ваги CF", fontsize=14)
    plt.xlabel("Вага Collaborative Filtering", fontsize=12)
    plt.ylabel(f"Precision@{TOP_K}", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('optimization_chart_real.png', dpi=300)
    print(f"✅ Графік збережено як optimization_chart_real.png")
    print(f"🏆 Найкраща вага для вашої системи: {best_weight}")

if __name__ == "__main__":
    run_experiment()