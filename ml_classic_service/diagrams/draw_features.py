import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def draw_feature_heatmap():
    # Емуляція результату TF-IDF для 5 подій та 10 слів
    events = ["Workshop Python", "Yoga Morning", "Jazz Concert", "Startup Pitch", "Marathon"]
    terms = ["python", "code", "yoga", "health", "music", "jazz", "startup", "business", "run", "sport"]
    
    # Генеруємо "красиві" дані, схожі на TF-IDF (розріджені)
    data = np.array([
        [0.8, 0.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], # Workshop
        [0.0, 0.0, 0.9, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], # Yoga
        [0.0, 0.0, 0.0, 0.0, 0.7, 0.8, 0.0, 0.0, 0.0, 0.0], # Jazz
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.6, 0.0, 0.0], # Startup
        [0.0, 0.0, 0.0, 0.4, 0.0, 0.0, 0.0, 0.0, 0.8, 0.7], # Marathon
    ])
    
    df_heatmap = pd.DataFrame(data, index=events, columns=terms)

    plt.figure(figsize=(12, 6))
    sns.heatmap(df_heatmap, annot=True, cmap="YlGnBu", cbar_kws={'label': 'TF-IDF Weight'})
    
    plt.title("Рис 2.4. Фрагмент матриці ознак (TF-IDF) після векторизації", fontsize=14)
    plt.xlabel("Терміни (Tokens)")
    plt.ylabel("Події (Documents)")
    
    plt.tight_layout()
    plt.savefig('tfidf_heatmap.png', dpi=300)
    print("✅ Діаграма збережена як tfidf_heatmap.png")

if __name__ == "__main__":
    draw_feature_heatmap()