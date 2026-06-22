# =============================================================
#  Аналіз датасету Last.fm (HetRec 2011) для слайдів презентації
# =============================================================
#  Рахує базову статистику сирого датасету та будує 4 графіки.
#  Працює ТІЛЬКИ з сирими файлами, які реально читають скрипти 1→5:
#    - user_artists.dat        (userID, artistID, weight) — прослуховування
#    - user_taggedartists.dat  (userID, artistID, tagID)  — теги
#    - tags.dat                (tagID, tagValue)           — назви тегів
#    - artists.dat             (id, name, ...)             — назви артистів
#
#  Виходи (data/analysis/):
#    - 01_listens_loghist.png   розподіл к-ті прослуховувань (log)
#    - 02_user_activity.png     активність на користувача
#    - 03_artist_longtail.png   популярність артистів (long tail)
#    - 04_tag_distribution.png  топ-тегів
#    - 00_overview.png          зведена панель 2x2
#    - dataset_summary.csv      зведена таблиця ключових чисел
# =============================================================

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family":  "DejaVu Sans",   # підтримує кирилицю
    "font.size":    12,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "figure.dpi":   200,
    "savefig.dpi":  200,
})

ACCENT  = "#4F46E5"
ACCENT2 = "#C2410C"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
OUT_DIR  = os.path.join(BASE_DIR, "data", "analysis")
os.makedirs(OUT_DIR, exist_ok=True)


def load():
    ua = pd.read_csv(os.path.join(RAW_DIR, "user_artists.dat"),
                     sep="\t", encoding="latin-1")
    uta = pd.read_csv(os.path.join(RAW_DIR, "user_taggedartists.dat"),
                      sep="\t", encoding="latin-1")
    tags = pd.read_csv(os.path.join(RAW_DIR, "tags.dat"),
                       sep="\t", encoding="latin-1")
    artists = pd.read_csv(os.path.join(RAW_DIR, "artists.dat"),
                          sep="\t", encoding="latin-1",
                          usecols=["id", "name"])
    return ua, uta, tags, artists


def main():
    ua, uta, tags, artists = load()

    # ── Базова статистика ──────────────────────────────────────
    n_users    = ua["userID"].nunique()
    n_artists  = ua["artistID"].nunique()
    n_inter    = len(ua)                          # пари (user, artist) з вагою
    n_tags_all = tags["tagID"].nunique()          # усі теги у словнику
    n_tags_use = uta["tagID"].nunique()           # теги, що реально використані
    n_tag_assign = len(uta)                       # призначень тегів

    sparsity = 1.0 - n_inter / (n_users * n_artists)
    density  = 100.0 * n_inter / (n_users * n_artists)

    # прослуховування на користувача (к-ть артистів + сумарна вага)
    per_user_cnt = ua.groupby("userID")["artistID"].count()
    per_user_sum = ua.groupby("userID")["weight"].sum()
    # популярність артистів (к-ть слухачів + сумарна вага)
    per_art_cnt  = ua.groupby("artistID")["userID"].count()
    per_art_sum  = ua.groupby("artistID")["weight"].sum()

    w = ua["weight"]

    # топ-10 артистів за сумарними прослуховуваннями
    art_name = artists.set_index("id")["name"]
    top_artists = (per_art_sum.sort_values(ascending=False).head(10)
                   .rename("total_plays").reset_index())
    top_artists["name"] = top_artists["artistID"].map(art_name).fillna("—")

    # топ-15 тегів за частотою використання
    tag_name = tags.set_index("tagID")["tagValue"]
    tag_freq = (uta["tagID"].map(tag_name)
                .value_counts().head(15).rename("count"))

    # ── Зведена таблиця ────────────────────────────────────────
    summary = pd.DataFrame({
        "Показник": [
            "Користувачів (users)",
            "Артистів (artists)",
            "Тегів у словнику (tags.dat)",
            "Тегів реально використано",
            "Призначень тегів (user-artist-tag)",
            "Взаємодій user-artist (рядків)",
            "Щільність матриці (density)",
            "Розрідженість (sparsity)",
            "Артистів/користувача — медіана",
            "Артистів/користувача — середнє",
            "Прослуховувань/користувача — медіана",
            "Слухачів/артиста — медіана",
            "Weight — медіана",
            "Weight — середнє",
            "Weight — максимум",
        ],
        "Значення": [
            f"{n_users:,}",
            f"{n_artists:,}",
            f"{n_tags_all:,}",
            f"{n_tags_use:,}",
            f"{n_tag_assign:,}",
            f"{n_inter:,}",
            f"{density:.3f}%",
            f"{sparsity*100:.3f}%",
            f"{per_user_cnt.median():.0f}",
            f"{per_user_cnt.mean():.1f}",
            f"{per_user_sum.median():,.0f}",
            f"{per_art_cnt.median():.0f}",
            f"{w.median():,.0f}",
            f"{w.mean():,.0f}",
            f"{w.max():,.0f}",
        ],
    })
    summary.to_csv(os.path.join(OUT_DIR, "dataset_summary.csv"),
                   index=False, encoding="utf-8-sig")

    # друк у консоль
    print("=" * 60)
    print("  ЗВЕДЕНА СТАТИСТИКА ДАТАСЕТУ Last.fm (HetRec 2011)")
    print("=" * 60)
    print(summary.to_string(index=False))
    print("\n  ТОП-10 АРТИСТІВ за сумарними прослуховуваннями:")
    for _, r in top_artists.iterrows():
        print(f"    {r['name'][:35]:<35} {int(r['total_plays']):>12,}")
    print("\n  ТОП-15 ТЕГІВ за частотою:")
    for name, cnt in tag_freq.items():
        print(f"    {str(name)[:35]:<35} {int(cnt):>8,}")

    # =====================================================
    #  ГРАФІК 1 — лог-розподіл прослуховувань (weight)
    # =====================================================
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bins = np.logspace(0, np.log10(w.max()), 50)
    ax.hist(w, bins=bins, color=ACCENT, alpha=0.85, edgecolor="white", linewidth=0.3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Кількість прослуховувань артиста одним користувачем (weight)")
    ax.set_ylabel("Кількість взаємодій (log)")
    ax.set_title("Розподіл прослуховувань (log–log)")
    ax.axvline(w.median(), color=ACCENT2, linestyle="--", linewidth=1.5,
               label=f"медіана = {w.median():,.0f}")
    ax.legend()
    ax.grid(True, which="both", alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "01_listens_loghist.png"))
    plt.close(fig)

    # =====================================================
    #  ГРАФІК 2 — активність на користувача
    # =====================================================
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.hist(per_user_cnt, bins=range(0, per_user_cnt.max() + 2),
            color=ACCENT, alpha=0.85, edgecolor="white", linewidth=0.3)
    ax.set_xlabel("Кількість артистів у профілі користувача")
    ax.set_ylabel("Кількість користувачів")
    ax.set_title("Активність на користувача")
    ax.axvline(per_user_cnt.mean(), color=ACCENT2, linestyle="--", linewidth=1.5,
               label=f"середнє = {per_user_cnt.mean():.1f}")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "02_user_activity.png"))
    plt.close(fig)

    # =====================================================
    #  ГРАФІК 3 — популярність артистів (long tail)
    # =====================================================
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ranked = per_art_cnt.sort_values(ascending=False).reset_index(drop=True)
    ax.plot(np.arange(1, len(ranked) + 1), ranked.values,
            color=ACCENT, linewidth=1.8)
    ax.fill_between(np.arange(1, len(ranked) + 1), ranked.values,
                    color=ACCENT, alpha=0.15)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Ранг артиста (від найпопулярнішого)")
    ax.set_ylabel("Кількість слухачів")
    ax.set_title("Популярність артистів: «довгий хвіст»")
    # позначка: скільки артистів мають лише 1 слухача
    one_listener = int((per_art_cnt == 1).sum())
    ax.annotate(f"{one_listener:,} артистів\nмають 1 слухача",
                xy=(len(ranked) * 0.55, 1.2),
                fontsize=10, color=ACCENT2)
    ax.grid(True, which="both", alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "03_artist_longtail.png"))
    plt.close(fig)

    # =====================================================
    #  ГРАФІК 4 — розподіл тегів (топ-15)
    # =====================================================
    fig, ax = plt.subplots(figsize=(7, 5))
    tf = tag_freq[::-1]   # щоб найбільший був зверху
    ax.barh(tf.index.astype(str), tf.values, color=ACCENT, alpha=0.85)
    ax.set_xlabel("Кількість призначень тегу")
    ax.set_title("Топ-15 тегів Last.fm за частотою")
    for i, v in enumerate(tf.values):
        ax.text(v, i, f" {int(v):,}", va="center", fontsize=9, color="#333")
    ax.grid(True, axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "04_tag_distribution.png"))
    plt.close(fig)

    # =====================================================
    #  ОГЛЯДОВА ПАНЕЛЬ 2x2
    # =====================================================
    fig, axs = plt.subplots(2, 2, figsize=(14, 9))

    a = axs[0, 0]
    a.hist(w, bins=bins, color=ACCENT, alpha=0.85)
    a.set_xscale("log"); a.set_yscale("log")
    a.set_title("Розподіл прослуховувань (log–log)")
    a.set_xlabel("weight"); a.set_ylabel("к-ть взаємодій")
    a.grid(True, which="both", alpha=0.2)

    a = axs[0, 1]
    a.hist(per_user_cnt, bins=range(0, per_user_cnt.max() + 2),
           color=ACCENT, alpha=0.85)
    a.set_title("Активність на користувача")
    a.set_xlabel("артистів у профілі"); a.set_ylabel("к-ть користувачів")
    a.grid(True, axis="y", alpha=0.2)

    a = axs[1, 0]
    a.plot(np.arange(1, len(ranked) + 1), ranked.values, color=ACCENT)
    a.fill_between(np.arange(1, len(ranked) + 1), ranked.values,
                   color=ACCENT, alpha=0.15)
    a.set_xscale("log"); a.set_yscale("log")
    a.set_title("Популярність артистів (long tail)")
    a.set_xlabel("ранг"); a.set_ylabel("к-ть слухачів")
    a.grid(True, which="both", alpha=0.2)

    a = axs[1, 1]
    a.barh(tf.index.astype(str), tf.values, color=ACCENT, alpha=0.85)
    a.set_title("Топ-15 тегів")
    a.set_xlabel("к-ть призначень")
    a.grid(True, axis="x", alpha=0.2)

    fig.suptitle("Датасет Last.fm (HetRec 2011) — розподіл даних",
                 fontsize=16, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(os.path.join(OUT_DIR, "00_overview.png"))
    plt.close(fig)

    print("\n  Графіки збережено в:", OUT_DIR)
    for f in sorted(os.listdir(OUT_DIR)):
        print("   -", f)


if __name__ == "__main__":
    main()
