#============================================================
# 1: Імпорт та налаштування
import pandas as pd
import numpy as np
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity
import warnings
import os
warnings.filterwarnings('ignore')

# Налаштування
INPUT_FILE = 'real_events_enriched.csv'
MODEL_FILE = 'models/recommendation_model.pkl'
RANDOM_STATE = 42

# --- НАЛАШТУВАННЯ СТОП-СЛІВ ---
# Беремо стандартні англійські стоп-слова
CUSTOM_STOP_WORDS = list(ENGLISH_STOP_WORDS)

# Видаляємо "it", щоб воно НЕ вважалося сміттям (бо для нас це категорія IT)
if "it" in CUSTOM_STOP_WORDS:
    CUSTOM_STOP_WORDS.remove("it")

# (Опціонально) Можна додати українські стоп-слова, якщо вони є в описах
UA_STOP_WORDS = ['і', 'та', 'на', 'в', 'для', 'з', 'по', 'до', 'це', 'як', 'що']
CUSTOM_STOP_WORDS.extend(UA_STOP_WORDS)
#============================================================
# 2: Завантаження даних
def load_data(filepath):
    """
    Завантажує підготовлений датасет.
    
    Returns:
        pd.DataFrame: датафрейм з подіями
    """
    print("=" * 60)
    print("КРОК 1: ЗАВАНТАЖЕННЯ ДАНИХ")
    print("=" * 60)
    
    if not os.path.exists(filepath):
        print(f"Помилка: Файл {filepath} не знайдено!")
        return None

    df = pd.read_csv(filepath, encoding='utf-8')
    
    print(f"✓ Завантажено рядків: {len(df)}")
    print(f"✓ Колонки: {list(df.columns)}")
    print(f"\nРозподіл по категоріях:")
    print(df['category'].value_counts().to_string())
    
    return df

#============================================================
# 3: Дослідницький аналіз даних (EDA)
def perform_eda(df):
    """
    Розвідувальний аналіз даних.
    """
    print("\n" + "=" * 60)
    print("КРОК 2: EXPLORATORY DATA ANALYSIS")
    print("=" * 60)
    
    # 1. Перевірка пропущених значень
    print("\n1. Пропущені значення:")
    print(df.isnull().sum())
    
    # 2. Дублікати
    duplicates = df.duplicated(subset=['description']).sum()
    print(f"\n2. Дублікати описів: {duplicates}")
    
    # 3. Статистика по довжині текстів
    df['text_length'] = df['description'].str.len()
    print(f"\n3. Довжина описів:")
    print(f"   Середня: {df['text_length'].mean():.1f} символів")
    print(f"   Мін: {df['text_length'].min()}")
    print(f"   Макс: {df['text_length'].max()}")
    
    # 4. Приклади даних
    print("\n4. Приклади даних (перші 3 рядки):")
    for idx, row in df.head(3).iterrows():
        print(f"\n   [{row['category']}] {row['description'][:100]}...")
    
    return df

#============================================================
# 4: Очищення тексту (Попередня обробка тексту)
def clean_text(text):
    """
    Очищає текст від зайвих символів.
    
    Args:
        text (str): вхідний текст
        
    Returns:
        str: очищений текст
    """
    # Приведення до нижнього регістру
    text = text.lower()
    
    # Видалення спецсимволів (залишаємо букви, цифри, пробіли)
    text = re.sub(r"[^a-zA-Zа-яА-ЯёЁіІїЇєЄ0-9\s'’]", ' ', text)
    
    # Видалення зайвих пробілів
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def preprocess_data(df):
    """
    Попередня обробка текстових даних.
    """
    print("\n" + "=" * 60)
    print("КРОК 3: PREPROCESSING (Очищення тексту)")
    print("=" * 60)
    
    # Заповнення пропущених значень
    df['description'] = df['description'].fillna('')
    df['category'] = df['category'].fillna('')

    print("✓ Об'єднання Категорії та Опису...")
    df['text_for_training'] = df['category'] + " " + df['description']

    # Очищення тексту
    print("✓ Очищення тексту...")
    df['cleaned_text'] = df['description'].apply(clean_text)
    
    # Перевірка результатів
    print("\nПриклад даних:")
    sample = df.iloc[0]
    print(f"Категорія: {sample['category']}")
    print(f"Текст для навчання: {sample['cleaned_text'][:100]}...")
    
    # Видалення порожніх рядків (якщо є)
    initial_len = len(df)
    df = df[df['cleaned_text'].str.len() > 0]
    if len(df) < initial_len:
        print(f"\n⚠ Видалено порожніх рядків: {initial_len - len(df)}")
    
    return df

#============================================================
# 5: Вилучення функцій (TF-IDF)
def extract_features(df):
    """
    Витягує ознаки за допомогою TF-IDF.
    
    Returns:
        tuple: (векторизатор, TF-IDF матриця)
    """
    print("\n" + "=" * 60)
    print("КРОК 4: FEATURE EXTRACTION (TF-IDF)")
    print("=" * 60)
    
    # Ініціалізація TF-IDF векторізатора
    vectorizer = TfidfVectorizer(
        max_features=5000,        # топ-5000 найважливіших слів
        ngram_range=(1, 2),       # 1-грами та 2-грами
        min_df=2,                 # слово має бути мінімум у 2 документах
        max_df=0.8,               # ігноруємо слова, що в >80% документів
        stop_words=CUSTOM_STOP_WORDS,          # можна додати українські/англійські
        sublinear_tf=True         # логарифмічне масштабування частот
    )
    
    # Векторизація
    print("\n✓ Векторизація текстів...")
    tfidf_matrix = vectorizer.fit_transform(df['cleaned_text'])
    
    print(f"✓ Розмір TF-IDF матриці: {tfidf_matrix.shape}")
    print(f"   - {tfidf_matrix.shape[0]} подій")
    print(f"   - {tfidf_matrix.shape[1]} унікальних термінів")
    print(f"   - Розрідженість: {(1 - tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1])) * 100:.2f}%")
    
    # Приклад найважливіших слів
    #feature_names = vectorizer.get_feature_names_out()
    #print(f"\nПриклад термінів (перші 20):")
    #print(feature_names[:20])
    if 'it' in vectorizer.vocabulary_:
        print(" Слово 'it' успішно додано до словника моделі.")
    else:
        print("Увага: Слово 'it' відсутнє у словнику (можливо, воно занадто рідкісне або часте).")

    return vectorizer, tfidf_matrix

#============================================================
# 6: Обчислення схожості (Cosine Similarity)
def compute_similarity(tfidf_matrix):
    """
    Обчислює матрицю косинусної подібності.
    
    Returns:
        np.ndarray: матриця схожості (n_events x n_events)
    """
    print("\n" + "=" * 60)
    print("КРОК 5: ОБЧИСЛЕННЯ СХОЖОСТІ (Cosine Similarity)")
    print("=" * 60)
    
    print("✓ Обчислення косинусної подібності...")
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    print(f"✓ Розмір матриці схожості: {similarity_matrix.shape}")
    print(f"   - Кожна подія порівняна з {similarity_matrix.shape[1] - 1} іншими")
    
    # Статистика
    # Зануляємо діагональ (схожість події сама з собою)
    np.fill_diagonal(similarity_matrix, 0)
    
    print(f"\nСтатистика схожості:")
    print(f"   Середня: {similarity_matrix.mean():.4f}")
    print(f"   Мін: {similarity_matrix.min():.4f}")
    print(f"   Макс: {similarity_matrix.max():.4f}")
    print(f"   Медіана: {np.median(similarity_matrix):.4f}")
    
    return similarity_matrix

#============================================================
# 7: Валідація моделі (Тестування)
def validate_model(df, similarity_matrix, n_recommendations=5):
    """
    Валідація моделі на тестових прикладах.
    """
    print("\n" + "=" * 60)
    print("КРОК 6: ВАЛІДАЦІЯ МОДЕЛІ")
    print("=" * 60)
    
    # Вибираємо випадкові події для тестування
    test_indices = np.random.choice(len(df), size=3, replace=False)
    
    for test_idx in test_indices:
        event = df.iloc[test_idx]
        
        print(f"\n{'─' * 60}")
        print(f"ТЕСТОВА ПОДІЯ #{test_idx}")
        print(f"Категорія: {event['category']}")
        print(f"Опис: {event['description'][:100]}...")
        
        # Отримуємо топ-N рекомендацій
        similarities = similarity_matrix[test_idx]
        top_indices = similarities.argsort()[-n_recommendations:][::-1]
        
        print(f"\nТоп-{n_recommendations} рекомендацій:")
        for i, idx in enumerate(top_indices, 1):
            rec_event = df.iloc[idx]
            score = similarities[idx]
            print(f"\n   {i}. [{rec_event['category']}] Схожість: {score:.4f}")
            print(f"      {rec_event['description'][:80]}...")

#============================================================
# 8: Збереження моделі
def save_model(df, vectorizer, tfidf_matrix, similarity_matrix, filepath):
    """
    Зберігає навчену модель у файл.
    """
    print("\n" + "=" * 60)
    print("КРОК 7: ЗБЕРЕЖЕННЯ МОДЕЛІ")
    print("=" * 60)
    
    model_data = {
        'events_df': df[['category', 'description', 'cleaned_text']].reset_index(drop=True),
        'vectorizer': vectorizer,
        'tfidf_matrix': tfidf_matrix,
        'similarity_matrix': similarity_matrix,
        'metadata': {
            'n_events': len(df),
            'n_features': vectorizer.max_features,
            'ngram_range': vectorizer.ngram_range,
            'tfidf_shape': tfidf_matrix.shape,
            'training_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    
    with open(filepath, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"✓ Модель збережена: {filepath}")
    print(f"✓ Розмір файлу: {os.path.getsize(filepath) / 1024 / 1024:.2f} MB")
    print(f"\nЗбережені компоненти:")
    print(f"   ✓ events_df: {len(df)} подій")
    print(f"   ✓ vectorizer: TfidfVectorizer")
    print(f"   ✓ tfidf_matrix: {tfidf_matrix.shape}")           # ← ДОДАНО
    print(f"   ✓ similarity_matrix: {similarity_matrix.shape}")
    print(f"\nМетадані:")
    for key, value in model_data['metadata'].items():
        print(f"   {key}: {value}")

#============================================================
#  9: Головна функція
def main():
    """
    Основна функція тренування моделі.
    """
    
    print("\n" + "=" * 60)
    print("ТРЕНУВАННЯ РЕКОМЕНДАЦІЙНОЇ СИСТЕМИ")
    print("=" * 60)
    
    # Перевірка існування файлу
    if not os.path.exists(INPUT_FILE):
        print(f" Файл не знайдено: {INPUT_FILE}")
        return
    
    # Створення директорії для моделі
    os.makedirs('models', exist_ok=True)
    
    # Виконання всіх кроків
    df = load_data(INPUT_FILE)
    if df is None: return
    df = perform_eda(df)
    df = preprocess_data(df)
    vectorizer, tfidf_matrix = extract_features(df)
    similarity_matrix = compute_similarity(tfidf_matrix)
    validate_model(df, similarity_matrix)
    save_model(df, vectorizer, tfidf_matrix, similarity_matrix, MODEL_FILE)
    
    print("\n" + "=" * 60)
    print(" ТРЕНУВАННЯ ЗАВЕРШЕНО УСПІШНО!")
    print("=" * 60)
    

if __name__ == "__main__":
    main()
