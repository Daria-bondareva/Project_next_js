import numpy as np
import matplotlib.pyplot as plt

def draw_radar_chart():
    # Категорії метрик
    categories = ['Accuracy\n(Precision)', 'Explainability', 'Cold Start\nHandling', 'Diversity', 'Scalability']
    N = len(categories)

    # Дані для моделей (оцінки від 1 до 5)
    # Hybrid - ваша модель (збалансована)
    values_hybrid = [4, 4, 4, 3, 3]
    # Content-Based (Класична) - чудова для Cold Start, але нудна (низька Diversity)
    values_cb = [3, 5, 5, 2, 4]
    # Collaborative Filtering - погано з Cold Start, але точна для старих юзерів
    values_cf = [5, 1, 1, 5, 2]

    # Замикаємо коло (повторюємо перше значення в кінці)
    values_hybrid += values_hybrid[:1]
    values_cb += values_cb[:1]
    values_cf += values_cf[:1]

    # Кути для осей
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    # Побудова
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    # 1. Hybrid (Ваша)
    ax.plot(angles, values_hybrid, linewidth=2, linestyle='solid', label='Hybrid Model (Kindred)', color='#4ECDC4')
    ax.fill(angles, values_hybrid, color='#4ECDC4', alpha=0.25)

    # 2. Content-Based
    ax.plot(angles, values_cb, linewidth=1, linestyle='dashed', label='Content-Based Only', color='#FF6B6B')
    
    # 3. Collaborative
    ax.plot(angles, values_cf, linewidth=1, linestyle='dotted', label='Collaborative Only', color='#45B7D1')

    # Налаштування осей
    plt.xticks(angles[:-1], categories, color='black', size=10)
    ax.set_rlabel_position(0)
    plt.yticks([1, 2, 3, 4, 5], ["1", "2", "3", "4", "5"], color="grey", size=7)
    plt.ylim(0, 5)

    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    
    # Прибираємо заголовок з картинки для дотримання стандартів оформлення
    # plt.title("Рис 3.1. Порівняння характеристик алгоритмів", ...)

    plt.tight_layout()
    plt.savefig('model_comparison_radar.png', dpi=300)
    print("✅ Діаграма збережена як model_comparison_radar.png")

if __name__ == "__main__":
    draw_radar_chart()