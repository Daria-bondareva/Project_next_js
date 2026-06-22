# =============================================================
#  Аналіз ПЕРЕТВОРЕНИХ даних Kindred (вихід pipeline, крок 1)
# =============================================================
#  Працює з data/processed/{users,events,interactions}.csv —
#  тобто з 13 власними тегами-категоріями, подіями та синтезованими
#  взаємодіями, які реально використовує застосунок (НЕ сирий Last.fm).
#
#  Виходи (data/analysis_processed/):
#    - 01_users_per_interest.png    користувачів на кожен інтерес
#    - 02_events_per_tag.png        подій на кожен тег
#    - 03_interactions_per_tag.png  взаємодій на кожен тег
#    - 04_counts_distribution.png   к-ть інтересів/користувача + тегів/подію
#    - 00_overview.png              панель 2x2
#    - processed_summary.csv        зведена таблиця чисел
# =============================================================

import os
import ast
from collections import Counter
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── Тема: світла, прозорий фон, зелений + графіт ──────────────
GREEN  = "#7CB342"
GRAPH  = "#2B2C30"
plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "font.size":        12,
    "axes.titlesize":   14,
    "axes.titleweight": "bold",
    "text.color":       GRAPH,
    "axes.labelcolor":  GRAPH,
    "axes.edgecolor":   GRAPH,
    "xtick.color":      GRAPH,
    "ytick.color":      GRAPH,
    "axes.titlecolor":  GRAPH,
    "figure.dpi":       200,
    "savefig.dpi":      200,
})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IN_DIR   = os.path.join(BASE_DIR, "data", "processed")
OUT_DIR  = os.path.join(BASE_DIR, "data", "analysis_processed")
os.makedirs(OUT_DIR, exist_ok=True)


def save(fig, name):
    """Зберегти з прозорим фоном (осі та фігура — без заливки)."""
    fig.patch.set_alpha(0.0)
    for ax in fig.axes:
        ax.patch.set_alpha(0.0)
    fig.savefig(os.path.join(OUT_DIR, name), transparent=True,
                bbox_inches="tight")
    plt.close(fig)


def bar(ax, labels, values, title, xlabel):
    y = np.arange(len(labels))
    ax.barh(y, values, color=GREEN, edgecolor=GRAPH, linewidth=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()                       # найбільший зверху
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    vmax = max(values) if len(values) else 1
    for i, v in enumerate(values):
        ax.text(v + vmax * 0.01, i, f"{int(v):,}", va="center",
                fontsize=9, color=GRAPH)
    ax.set_xlim(0, vmax * 1.15)
    ax.grid(True, axis="x", alpha=0.25, color=GRAPH)


def main():
    users = pd.read_csv(os.path.join(IN_DIR, "users.csv"), encoding="utf-8")
    events = pd.read_csv(os.path.join(IN_DIR, "events.csv"), encoding="utf-8")
    inter = pd.read_csv(os.path.join(IN_DIR, "interactions.csv"), encoding="utf-8")

    users["interests"] = users["interests"].apply(ast.literal_eval)
    events["tags"] = events["tags"].apply(ast.literal_eval)

    # ── К-ть на кожен тег ──────────────────────────────────────
    users_per_tag  = Counter(t for lst in users["interests"] for t in lst)
    events_per_tag = Counter(t for lst in events["tags"] for t in lst)

    # взаємодії на тег: кожна взаємодія успадковує ВСІ теги своєї події
    event_tags = events.set_index("event_id")["tags"].to_dict()
    inter_per_tag = Counter()
    for eid in inter["event_id"]:
        for t in event_tags.get(eid, []):
            inter_per_tag[t] += 1

    # повний список 13 тегів = усі теги подій
    all_tags = sorted(events_per_tag.keys(),
                      key=lambda t: events_per_tag[t], reverse=True)

    # ── Розподіли к-ті ─────────────────────────────────────────
    interests_per_user = users["interests"].apply(len)
    tags_per_event     = events["tags"].apply(len)

    # ── Зведена таблиця по тегах ───────────────────────────────
    table = pd.DataFrame({
        "Тег": all_tags,
        "Користувачів з інтересом": [users_per_tag.get(t, 0) for t in all_tags],
        "Подій з тегом":            [events_per_tag.get(t, 0) for t in all_tags],
        "Взаємодій з тегом":        [inter_per_tag.get(t, 0) for t in all_tags],
    })
    table.to_csv(os.path.join(OUT_DIR, "processed_summary.csv"),
                 index=False, encoding="utf-8-sig")

    # загальні числа
    totals = pd.DataFrame({
        "Показник": [
            "Користувачів (users.csv)",
            "Подій (events.csv)",
            "Взаємодій (interactions.csv)",
            "Унікальних тегів подій",
            "Тегів-інтересів у користувачів",
            "Інтересів/користувача — середнє",
            "Інтересів/користувача — медіана",
            "Тегів/подію — середнє",
            "Тегів/подію — медіана",
            "Score взаємодій — середнє",
            "Score взаємодій — медіана",
        ],
        "Значення": [
            f"{len(users):,}",
            f"{len(events):,}",
            f"{len(inter):,}",
            f"{len(events_per_tag)}",
            f"{len(users_per_tag)}",
            f"{interests_per_user.mean():.2f}",
            f"{interests_per_user.median():.0f}",
            f"{tags_per_event.mean():.2f}",
            f"{tags_per_event.median():.0f}",
            f"{inter['score'].mean():.4f}",
            f"{inter['score'].median():.4f}",
        ],
    })
    totals.to_csv(os.path.join(OUT_DIR, "processed_totals.csv"),
                  index=False, encoding="utf-8-sig")

    # друк
    print("=" * 64)
    print("  ПЕРЕТВОРЕНІ ДАНІ KINDRED — розподіл за 13 тегами")
    print("=" * 64)
    print(table.to_string(index=False))
    print("\n" + totals.to_string(index=False))

    # ── ГРАФІК 1 — користувачів на інтерес ─────────────────────
    fig, ax = plt.subplots(figsize=(7.5, 5))
    bar(ax, all_tags, [users_per_tag.get(t, 0) for t in all_tags],
        "Користувачів з кожним інтересом", "Кількість користувачів")
    save(fig, "01_users_per_interest.png")

    # ── ГРАФІК 2 — подій на тег ────────────────────────────────
    fig, ax = plt.subplots(figsize=(7.5, 5))
    bar(ax, all_tags, [events_per_tag.get(t, 0) for t in all_tags],
        "Подій з кожним тегом", "Кількість подій")
    save(fig, "02_events_per_tag.png")

    # ── ГРАФІК 3 — взаємодій на тег ────────────────────────────
    fig, ax = plt.subplots(figsize=(7.5, 5))
    bar(ax, all_tags, [inter_per_tag.get(t, 0) for t in all_tags],
        "Взаємодій з кожним тегом", "Кількість взаємодій")
    save(fig, "03_interactions_per_tag.png")

    # ── ГРАФІК 4 — розподіли к-ті ──────────────────────────────
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.8))
    a = axs[0]
    vc = interests_per_user.value_counts().sort_index()
    a.bar(vc.index, vc.values, color=GREEN, edgecolor=GRAPH, linewidth=0.6)
    a.set_title("К-ть інтересів на користувача")
    a.set_xlabel("Інтересів у профілі"); a.set_ylabel("Користувачів")
    a.set_xticks(range(0, int(interests_per_user.max()) + 1))
    a.axvline(interests_per_user.mean(), color=GRAPH, linestyle="--",
              linewidth=1.5, label=f"середнє = {interests_per_user.mean():.2f}")
    a.legend(); a.grid(True, axis="y", alpha=0.25, color=GRAPH)

    a = axs[1]
    vc = tags_per_event.value_counts().sort_index()
    a.bar(vc.index, vc.values, color=GREEN, edgecolor=GRAPH, linewidth=0.6)
    a.set_title("К-ть тегів на подію")
    a.set_xlabel("Тегів у події"); a.set_ylabel("Подій")
    a.set_xticks(range(0, int(tags_per_event.max()) + 1))
    a.axvline(tags_per_event.mean(), color=GRAPH, linestyle="--",
              linewidth=1.5, label=f"середнє = {tags_per_event.mean():.2f}")
    a.legend(); a.grid(True, axis="y", alpha=0.25, color=GRAPH)
    save(fig, "04_counts_distribution.png")

    # ── ОГЛЯДОВА ПАНЕЛЬ 2x2 ────────────────────────────────────
    fig, axs = plt.subplots(2, 2, figsize=(15, 11))
    bar(axs[0, 0], all_tags, [users_per_tag.get(t, 0) for t in all_tags],
        "Користувачів з інтересом", "користувачів")
    bar(axs[0, 1], all_tags, [events_per_tag.get(t, 0) for t in all_tags],
        "Подій з тегом", "подій")
    bar(axs[1, 0], all_tags, [inter_per_tag.get(t, 0) for t in all_tags],
        "Взаємодій з тегом", "взаємодій")
    a = axs[1, 1]
    vc = tags_per_event.value_counts().sort_index()
    a.bar(vc.index, vc.values, color=GREEN, edgecolor=GRAPH, linewidth=0.6)
    a.set_title("К-ть тегів на подію")
    a.set_xlabel("тегів у події"); a.set_ylabel("подій")
    a.grid(True, axis="y", alpha=0.25, color=GRAPH)
    fig.suptitle("Перетворені дані Kindred — розподіл за 13 тегами",
                 fontsize=17, fontweight="bold", color=GRAPH)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save(fig, "00_overview.png")

    print("\n  Збережено в:", OUT_DIR)
    for f in sorted(os.listdir(OUT_DIR)):
        print("   -", f)


if __name__ == "__main__":
    main()
