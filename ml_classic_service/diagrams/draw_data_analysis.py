import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# Налаштування стилю
sns.set_theme(style="whitegrid")

def analyze_data():
    try:
        df = pd.read_csv('real_events_enriched.csv')
    except:
        print("❌ Файл real_events_enriched.csv не знайдено.")
        return

    # --- 1. ГІСТОГРАМА РОЗПОДІЛУ КАТЕГОРІЙ ---
    plt.figure(figsize=(12, 6))
    ax = sns.countplot(y='category', data=df, order=df['category'].value_counts().index, palette='viridis')
    
    plt.title('Рис 2.1. Розподіл подій за категоріями в підготовленому датасеті', fontsize=14)
    plt.xlabel('Кількість подій')
    plt.ylabel('Категорія')
    
    # Додаємо цифри на барчиках
    for p in ax.patches:
        ax.annotate(f'{int(p.get_width())}', (p.get_width() + 20, p.get_y() + 0.6))

    plt.tight_layout()
    plt.savefig('category_distribution.png', dpi=300)
    print("✅ Гістограма збережена: category_distribution.png")

    # --- 2. ХМАРА СЛІВ (WORD CLOUD) ---
    # Об'єднуємо всі описи в один текст
    text = " ".join(description for description in df.description.astype(str))
    
    wordcloud = WordCloud(width=1600, height=800, background_color='white', colormap='magma').generate(text)
    
    plt.figure(figsize=(14, 7))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Рис 2.2. Візуалізація семантичного ядра описів подій (Word Cloud)', fontsize=14, y=1.02)
    
    plt.tight_layout()
    plt.savefig('wordcloud.png', dpi=300)
    print("✅ Хмара слів збережена: wordcloud.png")

if __name__ == "__main__":
    analyze_data()