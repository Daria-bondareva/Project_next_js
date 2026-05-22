import numpy as np
import pickle
import os
from pymongo import MongoClient
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "../.env.local"))

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/testLogin")
MDL_DIR = os.path.join(BASE_DIR, "models")
K = 5  # k < min(45, 20) = 20, тому 5 — достатньо для малої матриці

print("=" * 60)
print("  STEP 6 - Retrain collab model on MongoDB data")
print("=" * 60)

# ── 1. З'єднання ───────────────────────────────────────────────
client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db = client.get_default_database()
events_col = db["events"]

client.admin.command("ping")
print("\nMongoDB: connected")

# ── 2. Читаємо всі події + participants ────────────────────────
print("\nLoading events from MongoDB...")
events_raw = list(events_col.find({}, {"_id": 1, "participants": 1}))
print(f"  Total events: {len(events_raw)}")

# ── 3. Збираємо унікальні ID і пари (user, event) ─────────────
all_event_ids = []   # порядок стабільний — відповідає стовпцям матриці
all_user_ids_set = set()
pairs = []           # (user_id_str, event_id_str)

for ev in events_raw:
    eid = str(ev["_id"])
    all_event_ids.append(eid)
    for uid in ev.get("participants", []):
        uid_str = str(uid)
        all_user_ids_set.add(uid_str)
        pairs.append((uid_str, eid))

all_user_ids = sorted(all_user_ids_set)  # стабільний порядок

print(f"  Unique users  (from participants): {len(all_user_ids)}")
print(f"  Events with participants: {sum(1 for e in events_raw if e.get('participants'))}")
print(f"  Total interactions (pairs):       {len(pairs)}")

# ── 4. Маппінги ObjectId-string → індекс ──────────────────────
user2idx  = {uid: i for i, uid in enumerate(all_user_ids)}
event2idx = {eid: i for i, eid in enumerate(all_event_ids)}

n_users  = len(all_user_ids)
n_events = len(all_event_ids)
print(f"\n  Interaction matrix: {n_users} x {n_events}")

# ── 5. Будуємо sparse interaction matrix ──────────────────────
rows, cols, data = [], [], []
for uid_str, eid_str in pairs:
    rows.append(user2idx[uid_str])
    cols.append(event2idx[eid_str])
    data.append(1.0)

interaction_matrix = csr_matrix(
    (data, (rows, cols)),
    shape=(n_users, n_events),
    dtype=float,
)
density = interaction_matrix.nnz / (n_users * n_events) * 100
print(f"  Non-zero elements: {interaction_matrix.nnz}")
print(f"  Density:           {density:.2f}%")

# ── 6. SVD (k < min(n_users, n_events)) ───────────────────────
k = min(K, min(n_users, n_events) - 1)
print(f"\nSVD decomposition (k={k})...")

U, sigma, Vt = svds(interaction_matrix, k=k)
sigma_diag      = np.diag(sigma)
predicted_scores = np.dot(np.dot(U, sigma_diag), Vt)  # shape: n_users x n_events

print(f"  U: {U.shape}  sigma: {sigma.shape}  Vt: {Vt.shape}")
print(f"  predicted_scores: {predicted_scores.shape}")
print(f"  min={predicted_scores.min():.4f}  max={predicted_scores.max():.4f}  mean={predicted_scores.mean():.4f}")

# ── 7. Зберігаємо нову modель ──────────────────────────────────
collab_model_mongodb = {
    "predicted_scores": predicted_scores,
    "user2idx":         user2idx,
    "event2idx":        event2idx,
    "user_ids":         all_user_ids,
    "event_ids":        all_event_ids,
    "U":                U,
    "sigma":            sigma,
    "Vt":               Vt,
    "k":                k,
}

out_path = os.path.join(MDL_DIR, "collab_model_mongodb.pkl")
with open(out_path, "wb") as f:
    pickle.dump(collab_model_mongodb, f)

print(f"\n  Saved: collab_model_mongodb.pkl")

# ── 8. Smoke-test: перший юзер → топ-3 події ──────────────────
print("\nSmoke test (first user in matrix):")
sample_uid = all_user_ids[0]
sample_scores = predicted_scores[user2idx[sample_uid]]
top3_idx = np.argsort(sample_scores)[::-1][:3]
print(f"  user: ...{sample_uid[-8:]}")
for rank, i in enumerate(top3_idx, 1):
    print(f"  #{rank}  event ...{all_event_ids[i][-8:]}  score={sample_scores[i]:.4f}")

client.close()
print("\n" + "=" * 60)
print("  STEP 6 DONE")
print("  Restart FastAPI (uvicorn main:app --reload) to apply changes.")
print("=" * 60)
