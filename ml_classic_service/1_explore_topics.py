# ml_classic_service/explore_topics.py

import pandas as pd

FILENAME = 'event_dataset.csv'

def explore():
    print(f" Читаємо вибірку з {FILENAME}...")
    
    try:
        # Читаємо перші 100,000 рядків. Це дасть репрезентативну картину.
        # encoding='latin1' потрібен для старих датасетів, якщо utf-8 не спрацює
        df = pd.read_csv(FILENAME, nrows=100000, encoding='latin1') 
    except Exception as e:
        print(f" Помилка: {e}")
        return

    print("\n Знайдені колонки:")
    print(df.columns.tolist())

    # Список колонок, де потенційно можуть бути категорії
    # Скрипт перевірить їх усі
    potential_columns = ['Topic', 'Event Type', 'Category', 'Group Category', 'Tags']

    found_target_col = False

    for col in potential_columns:
        if col in df.columns:
            found_target_col = True
            print(f"\n  ТОП-50 значень у колонці '{col}':")
            print("-" * 40)
            # value_counts() рахує унікальні значення і сортує за частотою
            print(df[col].value_counts().head(50).to_string())
            print("-" * 40)

    if not found_target_col:
        print("\n Не знайдено очевидних колонок з категоріями.")
        print("Подивіться на список колонок вище і змініть список 'potential_columns' у скрипті.")

if __name__ == "__main__":
    explore()