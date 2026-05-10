import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_ensemble():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    ax.axis('off')

    # Функція для малювання блоку
    def draw_box(x, y, w, h, text, color='#E0E0E0', title=""):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2", 
                                      linewidth=1.5, edgecolor='#333', facecolor=color)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=10, fontweight='bold')
        if title:
            ax.text(x + w/2, y + h + 1, title, ha='center', fontsize=9, style='italic')

    # --- INPUT LAYER ---
    draw_box(5, 35, 15, 8, "User Data\n(Interests + History)", '#FFECB3')
    draw_box(5, 15, 15, 8, "Event Data\n(Tags + Participants)", '#FFECB3')

    # --- BASE MODELS (Level 0) ---
    draw_box(30, 35, 20, 8, "Content-Based\nModel (TF-IDF)", '#B3E5FC', "Model A")
    draw_box(30, 15, 20, 8, "Collaborative\nFiltering (User-KNN)", '#B3E5FC', "Model B")

    # Стрілки до моделей
    ax.arrow(21, 39, 8, 0, head_width=1, fc='gray', ec='gray')
    ax.arrow(21, 19, 8, 0, head_width=1, fc='gray', ec='gray')
    ax.arrow(21, 39, 8.5, -18, head_width=0, fc='gray', ec='gray', linestyle='--') # Cross data
    ax.arrow(21, 19, 8.5, 18, head_width=0, fc='gray', ec='gray', linestyle='--')

    # --- ENSEMBLE LAYER (Level 1) ---
    draw_box(60, 25, 15, 8, "Weighted\nBlending\n(10*CB + 5*CF)", '#C8E6C9', "Ensemble")

    # Стрілки до ансамблю
    ax.arrow(51, 39, 8, -8, head_width=1, fc='k', ec='k')
    ax.text(54, 38, "Score A", fontsize=9)
    ax.arrow(51, 19, 8, 8, head_width=1, fc='k', ec='k')
    ax.text(54, 21, "Score B", fontsize=9)

    # --- DOMAIN KNOWLEDGE (Post-Processing) ---
    draw_box(80, 25, 15, 8, "Domain Rules\n(Filters & Context)", '#FFCCBC', "Post-Process")

    # Стрілка
    ax.arrow(76, 29, 3, 0, head_width=1, fc='k', ec='k')

    # --- OUTPUT ---
    draw_box(80, 10, 15, 6, "Final\nRecommendations", '#D1C4E9')
    ax.arrow(87.5, 24, 0, -7, head_width=1, fc='k', ec='k')

    # Анотації
    ax.text(50, 48, "Architecture: Weighted Hybrid Ensemble", ha='center', fontsize=14, fontweight='bold')
    
    # Легенда
    ax.text(5, 5, "Domain Knowledge Rules:\n1. No past events\n2. No self-created events\n3. Time-of-day penalty", 
            fontsize=10, bbox=dict(facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig('ensemble_architecture.png', dpi=300)
    print("✅ Діаграма збережена як ensemble_architecture.png")

if __name__ == "__main__":
    draw_ensemble()