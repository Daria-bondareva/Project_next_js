# recsys_service/real_evaluation_charts.py

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import roc_curve, auc
import os
from dotenv import load_dotenv

# --- НАЛАШТУВАННЯ ---
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client.get_database()

# Ваги (як в main.py)
CF_WEIGHT = 5
CB_WEIGHT = 10

def calculate_cb_score(event_tags, user_interests):
    if not event_tags or not user_interests: return 0
    intersection = set(event_tags).intersection(set(user_interests))
    return (len(intersection) / max(len(event_tags), 1)) * CB_WEIGHT

def run_full_evaluation():
    print("🚀 ПОЧАТОК ГЕНЕРАЦІЇ РЕАЛЬНИХ ГРАФІКІВ...")

    # 1. ЗАВАНТАЖЕННЯ ДАНИХ
    events = list(db.events.find())
    users = list(db.users.find())
    events_df = pd.DataFrame(events)
    events_df['_id'] = events_df['_id'].astype(str)
    
    # Preprocessing
    if 'tags' not in events_df.columns: events_df['tags'] = [[] for _ in range(len(events_df))]
    else: events_df['tags'] = events_df['tags'].apply(lambda x: x if isinstance(x, list) else [])
    
    if 'participants' not in events_df.columns: events_df['participants'] = [[] for _ in range(len(events_df))]
    else: events_df['participants'] = events_df['participants'].apply(lambda x: [str(p) for p in x] if isinstance(x, list) else [])

    all_user_ids = [str(u['_id']) for u in users]
    all_event_ids = events_df['_id'].tolist()

    # 2. МАТРИЦЯ (для CF)
    print("📊 Будуємо матриці...")
    user_item_matrix = pd.DataFrame(0, index=all_user_ids, columns=all_event_ids)
    for _, event in events_df.iterrows():
        evt_id = event['_id']
        for p in event['participants']:
            if p in all_user_ids:
                user_item_matrix.loc[p, evt_id] = 1

    cosine_sim_matrix = cosine_similarity(user_item_matrix)
    similarity_df = pd.DataFrame(cosine_sim_matrix, index=all_user_ids, columns=all_user_ids)

    # 3. ЗБІР ДАНИХ ДЛЯ ГРАФІКІВ
    # Нам треба накопичити y_true та y_scores для ROC
    # Та Precision для різних K
    
    y_true_all = []
    y_score_hybrid = []
    y_score_cb = [] # Чистий Content-Based (для порівняння)
    
    precisions_hybrid = {1: [], 3: [], 5: [], 10: [], 20: []}
    precisions_cb = {1: [], 3: [], 5: [], 10: [], 20: []}

    print(f"🔄 Тестування на {len(users)} користувачах...")

    for user in users:
        user_id = str(user['_id'])
        user_interests = user.get('interests', [])
        
        # Історія
        user_vector = user_item_matrix.loc[user_id]
        history = user_vector[user_vector == 1].index.tolist()
        
        if len(history) < 2: continue

        # Leave-One-Out
        hidden_event = history[-1]
        visible_history = set(history[:-1])

        # --- A. Рахуємо бали (CF part) ---
        # "Чесний" CF без leakage (як ми робили в evaluate.py)
        test_vector = user_vector.copy().values.reshape(1, -1)
        # Зануляємо приховану
        hidden_idx = user_item_matrix.columns.get_loc(hidden_event)
        test_vector[0, hidden_idx] = 0
        
        sim_scores = cosine_similarity(test_vector, user_item_matrix.values)[0]
        sim_series = pd.Series(sim_scores, index=all_user_ids)
        top_peers = sim_series.drop(user_id).sort_values(ascending=False).head(10)
        
        cf_scores_map = {}
        for peer, sim in top_peers.items():
            if sim <= 0: continue
            peer_hist = user_item_matrix.loc[peer]
            for evt in peer_hist[peer_hist==1].index:
                if evt not in visible_history:
                    cf_scores_map[evt] = cf_scores_map.get(evt, 0) + (sim * CF_WEIGHT)

        # --- B. Рахуємо фінальні списки ---
        hybrid_scores = []
        cb_scores = []
        
        # Беремо Hidden Event + 50 випадкових негативних (для ROC)
        # (Бо рахувати для всіх подій довго, беремо семпл)
        negatives = [e for e in all_event_ids if e != hidden_event and e not in visible_history]
        import random
        if len(negatives) > 50: negatives = random.sample(negatives, 50)
        
        test_candidates = [hidden_event] + negatives
        
        for evt_id in test_candidates:
            # Знаходимо подію в DF
            event_row = events_df[events_df['_id'] == evt_id].iloc[0]
            
            # CB Score
            cb = calculate_cb_score(event_row['tags'], user_interests)
            
            # CF Score
            cf = cf_scores_map.get(evt_id, 0)
            
            # Hybrid
            hybrid = cb + cf
            
            # Зберігаємо для ROC (1 для hidden, 0 для negatives)
            is_target = 1 if evt_id == hidden_event else 0
            y_true_all.append(is_target)
            y_score_hybrid.append(hybrid)
            y_score_cb.append(cb)
            
            # Зберігаємо для Precision (tuple: id, score)
            hybrid_scores.append((evt_id, hybrid))
            cb_scores.append((evt_id, cb))

        # --- C. Рахуємо Precision@K для цього юзера ---
        # Сортуємо весь список
        hybrid_scores.sort(key=lambda x: x[1], reverse=True)
        cb_scores.sort(key=lambda x: x[1], reverse=True)
        
        for k in precisions_hybrid.keys():
            # Hybrid
            top_k_hybrid = [x[0] for x in hybrid_scores[:k]]
            precisions_hybrid[k].append(1 if hidden_event in top_k_hybrid else 0)
            
            # Classic CB
            top_k_cb = [x[0] for x in cb_scores[:k]]
            precisions_cb[k].append(1 if hidden_event in top_k_cb else 0)

    # 4. МАЛЮВАННЯ ГРАФІКІВ
    print("🎨 Генерація зображень...")
    
    # --- ROC CURVE ---
    fpr_hyb, tpr_hyb, _ = roc_curve(y_true_all, y_score_hybrid)
    roc_auc_hyb = auc(fpr_hyb, tpr_hyb)
    
    fpr_cb, tpr_cb, _ = roc_curve(y_true_all, y_score_cb)
    roc_auc_cb = auc(fpr_cb, tpr_cb)

    plt.figure(figsize=(10, 8))
    plt.plot(fpr_hyb, tpr_hyb, color='#4ECDC4', lw=3, label=f'Hybrid Model (AUC = {roc_auc_hyb:.2f})')
    plt.plot(fpr_cb, tpr_cb, color='#FF6B6B', lw=2, linestyle='--', label=f'Content-Based Only (AUC = {roc_auc_cb:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle=':', label='Random Guess')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('Рис 4.1. ROC-крива (На реальних даних)', fontsize=14)
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.savefig('roc_curve_real.png', dpi=300)
    print("✅ Збережено: roc_curve_real.png")

    # --- PRECISION @ K ---
    k_values = [1, 3, 5, 10, 20]
    avg_prec_hybrid = [np.mean(precisions_hybrid[k]) for k in k_values]
    avg_prec_cb = [np.mean(precisions_cb[k]) for k in k_values]
    
    plt.figure(figsize=(10, 6))
    plt.plot(k_values, avg_prec_hybrid, marker='o', lw=2, color='#4ECDC4', label='Hybrid Model')
    plt.plot(k_values, avg_prec_cb, marker='s', lw=2, linestyle='--', color='#FF6B6B', label='Content-Based Only')
    
    plt.title('Рис 4.2. Залежність Precision від K (На реальних даних)', fontsize=14)
    plt.xlabel('K', fontsize=12)
    plt.ylabel('Precision', fontsize=12)
    plt.xticks(k_values)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('precision_k_curve_real.png', dpi=300)
    print("✅ Збережено: precision_k_curve_real.png")

if __name__ == "__main__":
    run_full_evaluation()