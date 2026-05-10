import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_nlp_pipeline():
    # Збільшуємо ширину полотна, щоб нічого не обрізалося
    fig, ax = plt.subplots(figsize=(15, 6))
    
    # Налаштування осей (робимо запас по краях)
    ax.set_xlim(-5, 115) 
    ax.set_ylim(0, 45)
    ax.axis('off')

    # Параметри блоків
    box_w, box_h = 18, 12 # Трохи вищі блоки, щоб вліз текст
    y_pos = 18
    gap = 4
    
    # Кроки пайплайну
    steps = [
        ("Raw Input", "HTML, Emoji,\nUpper Case"),
        ("Normalization", "Lowercasing\nstr.lower()"),
        ("Cleaning", "Regex Filter\n[^a-zA-Z...]"),
        ("Tokenization", "Stop-words\nRemoval"),
        ("Clean Output", "Ready for\nTF-IDF")
    ]
    
    colors = ['#FFD1DC', '#FFECB3', '#D1C4E9', '#B3E5FC', '#C8E6C9']

    for i, (title, desc) in enumerate(steps):
        # Розрахунок позиції X з більшими відступами
        x_pos = i * (box_w + gap) + 5
        
        # Стрілка (малюємо перед блоком, починаючи з другого)
        if i > 0:
            arrow_start_x = x_pos - gap
            ax.arrow(arrow_start_x, y_pos + box_h/2, gap, 0, 
                     head_width=2, head_length=1.5, fc='gray', ec='gray', length_includes_head=True)

        # Блок (з тінню для краси)
        # Тінь
        shadow = patches.FancyBboxPatch((x_pos+0.5, y_pos-0.5), box_w, box_h, 
                                      boxstyle="round,pad=0.2", 
                                      linewidth=0, facecolor='#DDDDDD', zorder=1)
        ax.add_patch(shadow)

        # Основний блок
        rect = patches.FancyBboxPatch((x_pos, y_pos), box_w, box_h, 
                                      boxstyle="round,pad=0.2", 
                                      linewidth=1.5, edgecolor='#333', facecolor=colors[i], zorder=2)
        ax.add_patch(rect)
        
        # Текст (центруємо відносно блоку)
        center_x = x_pos + box_w/2
        center_y = y_pos + box_h/2
        
        ax.text(center_x, center_y + 2.5, title, 
                ha='center', va='center', fontsize=11, fontweight='bold', zorder=3)
        ax.text(center_x, center_y - 2, desc, 
                ha='center', va='center', fontsize=9, style='italic', zorder=3)

    # Приклад даних знизу (в окремій рамці)
    ax.text(55, 8, 'Example: "<h1>MEGA Party!!!</h1>"  →  "mega party"', 
            ha='center', va='center', fontsize=12, fontweight='bold', 
            bbox=dict(facecolor='#F5F5F5', edgecolor='gray', boxstyle='round,pad=0.6'))

    # Заголовок прибираємо, бо за вимогами ДСТУ він буде внизу в Word
    # plt.title("Рис 2.3. Пайплайн попередньої обробки", y=0.95, fontsize=14)

    plt.tight_layout()
    plt.savefig('nlp_pipeline.png', dpi=300, bbox_inches='tight') # bbox_inches='tight' обрізає зайве біле поле
    print("✅ Діаграма збережена як nlp_pipeline.png")

if __name__ == "__main__":
    draw_nlp_pipeline()