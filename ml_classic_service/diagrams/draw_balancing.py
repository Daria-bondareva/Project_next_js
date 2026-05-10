import matplotlib.pyplot as plt
import numpy as np

def draw_balancing_scheme():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Дані "ДО" (імітація реального дисбалансу з Kaggle)
    categories = ['Business', 'Politics', 'Music', 'Education', 'Sport', 'Gaming']
    counts_before = [14000, 12000, 8000, 5000, 100, 50] # Спорт і Геймінг майже відсутні
    
    # Дані "ПІСЛЯ" (Ваш результат)
    counts_after = [2000, 2000, 2000, 2000, 2000, 2000] # Ідеальний баланс
    
    colors_before = ['#FF9999' if c < 1000 else '#66B2FF' for c in counts_before]
    colors_after = ['#99FF99' for _ in counts_after]

    # Графік 1: ДО
    ax1.barh(categories, counts_before, color=colors_before)
    ax1.set_title('А. Вихідний розподіл класів (Imbalanced)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Кількість подій')
    ax1.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Додаємо анотації проблем
    ax1.annotate('Undersampling\nneeded', xy=(14000, 0), xytext=(10000, 0.5),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    ax1.annotate('Augmentation\nneeded', xy=(100, 4), xytext=(2000, 4.5),
                 arrowprops=dict(facecolor='red', shrink=0.05))

    # Графік 2: ПІСЛЯ
    ax2.barh(categories, counts_after, color=colors_after)
    ax2.set_title('Б. Розподіл після балансування (Balanced)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Кількість подій')
    ax2.set_xlim(0, 15000) # Той самий масштаб для порівняння
    ax2.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Лінія ліміту
    ax2.axvline(x=2000, color='red', linestyle='--', label='LIMIT_PER_CATEGORY')
    ax2.legend()

    plt.suptitle("Рис 2.5. Схема балансування класів у датасеті Kindred", fontsize=14)
    plt.tight_layout()
    plt.savefig('balancing_scheme.png', dpi=300)
    print("✅ Діаграма збережена як balancing_scheme.png")

if __name__ == "__main__":
    draw_balancing_scheme()