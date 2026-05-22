import sys
import os
import pickle
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

MDL_DIR = os.path.join(BASE_DIR, "models")

# ── 1. Завантаження моделей ────────────────────────────────────
with open(os.path.join(MDL_DIR, "collab_model_mongodb.pkl"), "rb") as f:
    collab_model = pickle.load(f)

with open(os.path.join(MDL_DIR, "best_weights.pkl"), "rb") as f:
    best_weights = pickle.load(f)

print("=" * 62)
print("  COLLAB FILTERING — END-TO-END TEST")
print("=" * 62)
print(f"\n  Collab matrix : {len(collab_model['user_ids'])} users x {len(collab_model['event_ids'])} events")
print(f"  SVD k         : {collab_model['k']}")
print(f"  Best weights  : content={best_weights['content_weight']}, collab={best_weights['collab_weight']}")

# ── 2. Беремо першого реального юзера ─────────────────────────
real_user_id = collab_model["user_ids"][0]
print(f"\n  Test user ObjectId : {real_user_id}")

# ── 3. Беремо всі події через db.py ───────────────────────────
from db import get_user_interests, get_all_events

mongo_events = get_all_events()

# Видаляємо події самого юзера (як у recommender.py)
mongo_events = [
    e for e in mongo_events
    if e.get("userId", {}).get("_id", "") != real_user_id
]

print(f"  Events available   : {len(mongo_events)}")

# Інтереси юзера з MongoDB
user_interests = get_user_interests(real_user_id)
print(f"  User interests     : {user_interests or '(empty)'}")

# ── 4. Score-функції ───────────────────────────────────────────
def minmax(arr: np.ndarray) -> np.ndarray:
    rng = arr.max() - arr.min()
    return (arr - arr.min()) / rng if rng > 0 else arr

def content_scores(interests, events):
    iset = set(interests)
    scores = np.zeros(len(events))
    for i, ev in enumerate(events):
        tags = set(ev.get("tags", []))
        union = iset | tags
        if union:
            scores[i] = len(iset & tags) / len(union)
    return scores

def collab_scores(user_id, events):
    scores = np.zeros(len(events))
    u2i = collab_model["user2idx"]
    e2i = collab_model["event2idx"]
    pred = collab_model["predicted_scores"]
    if user_id not in u2i:
        return scores
    row = pred[u2i[user_id]]
    for i, ev in enumerate(events):
        eid = str(ev.get("_id", ""))
        if eid in e2i:
            scores[i] = row[e2i[eid]]
    return scores

# ── Розраховуємо всі три набори скорів ────────────────────────
c_raw = content_scores(user_interests, mongo_events)
f_raw = collab_scores(real_user_id, mongo_events)

c_norm = minmax(c_raw)
f_norm = minmax(f_raw)

cw = best_weights["content_weight"]   # 0.8
fw = best_weights["collab_weight"]    # 0.2

scores_content_only = c_norm
scores_collab_only  = f_norm
scores_hybrid       = cw * c_norm + fw * f_norm

def top5(scores, mongo_events, score_label):
    top_idx = np.argsort(scores)[::-1][:5]
    result = []
    for rank, i in enumerate(top_idx, 1):
        ev = mongo_events[i]
        result.append({
            "rank":  rank,
            "idx":   i,
            "title": (ev.get("title") or "")[:38],
            "tags":  ev.get("tags", []),
            "score": scores[i],
            "_id":   str(ev["_id"]),
        })
    return result

top_content = top5(scores_content_only, mongo_events, "content")
top_collab  = top5(scores_collab_only,  mongo_events, "collab")
top_hybrid  = top5(scores_hybrid,       mongo_events, "hybrid")

# ── 5. Вивід ──────────────────────────────────────────────────
SEP = "-" * 62

def print_table(title, rows, score_label):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)
    print(f"  {'#':<3} {'Score':>7}  {'Title':<38}  Tags")
    print(f"  {'-'*3}  {'-'*7}  {'-'*38}  {'-'*15}")
    for r in rows:
        tags_str = ", ".join(r["tags"])[:20] if r["tags"] else "(no tags)"
        print(f"  {r['rank']:<3} {r['score']:>7.4f}  {r['title']:<38}  {tags_str}")

print_table(
    "CONTENT ONLY  (alpha_content=1.0, alpha_collab=0.0)",
    top_content, "content_score"
)
print_table(
    "COLLAB ONLY   (alpha_content=0.0, alpha_collab=1.0)",
    top_collab, "collab_score"
)
print_table(
    f"HYBRID        (alpha_content={cw}, alpha_collab={fw})",
    top_hybrid, "hybrid_score"
)

# ── 6. Аналіз різниці ─────────────────────────────────────────
ids_content = {r["_id"] for r in top_content}
ids_collab  = {r["_id"] for r in top_collab}
ids_hybrid  = {r["_id"] for r in top_hybrid}

only_in_collab  = ids_collab  - ids_content   # є в collab, нема в content
collab_added    = ids_hybrid  - ids_content   # з'явились у гібриді завдяки collab
content_dropped = ids_content - ids_hybrid    # були в content, зникли в гібриді

lists_differ = ids_content != ids_hybrid

print(f"\n{SEP}")
print("  ANALYSIS")
print(SEP)
print(f"  Lists differ (content vs hybrid) : {'YES' if lists_differ else 'NO — collab has no effect'}")
print(f"  Events only in collab top-5      : {len(only_in_collab)}")
print(f"  Events added to hybrid by collab : {len(collab_added)}")
print(f"  Events dropped from content top  : {len(content_dropped)}")

if collab_added:
    print(f"\n  Events that APPEAR in hybrid thanks to collab:")
    for r in top_hybrid:
        if r["_id"] in collab_added:
            tags_str = ", ".join(r["tags"])[:25] if r["tags"] else "(no tags)"
            print(f"    #{r['rank']}  {r['title']:<38}  [{tags_str}]")

if content_dropped:
    print(f"\n  Events DISPLACED from content-only top-5:")
    for r in top_content:
        if r["_id"] in content_dropped:
            tags_str = ", ".join(r["tags"])[:25] if r["tags"] else "(no tags)"
            print(f"    #{r['rank']}  {r['title']:<38}  [{tags_str}]")

collab_non_zero = (f_raw != 0).sum()
print(f"\n  Collab non-zero scores : {collab_non_zero}/{len(mongo_events)} events")
print(f"  Collab score range     : min={f_raw.min():.4f}  max={f_raw.max():.4f}")
print(f"  Content score range    : min={c_raw.min():.4f}  max={c_raw.max():.4f}")
print(f"\n{SEP}\n")
