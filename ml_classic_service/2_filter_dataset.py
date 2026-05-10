import pandas as pd
import os
import random

FILENAME = 'event_dataset.csv'
OUTPUT_FILE = 'real_events_enriched.csv'
LIMIT_PER_CATEGORY = 2000

# 1. Словник пошуку (Kaggle -> Наші категорії)
TARGET_CATEGORIES = {
    "IT": ["Technology"],
    "МУЗИКА": ["Music", "Concert"],
    "МИСТЕЦТВО": ["Art"],
    "БІЗНЕС": ["Business", "Conference"],
    "НАУКА": ["Education"], 
    "ОСВІТА": ["Workshop", "Seminar"],
    "РОЗВАГИ": ["Fun", "Birthday", "Party"],
    "СПОРТ": ["Valedictory"], 
    "ПОЛІТИКА": ["Politics"],
    "ЛЕКЦІЯ": ["Conference"]
}

# 2. Шаблони описів (ТЕПЕР З КЛЮЧОВИМИ СЛОВАМИ!)
DESCRIPTION_TEMPLATES = {
    "IT": [
        "Масштабна IT-конференція та хакатон. Формат: ОНЛАЙН.",
        "Воркшоп для розробників. Тема: IT та програмування.",
        "Зустріч спільноти. Обговорюємо IT тренди."
    ],
    "МУЗИКА": [
        "Живий концерт. Найкраща МУЗИКА цього сезону.",
        "Музичний фестиваль просто неба. ВЕЧІР джазу.",
        "Виступ гурту. Категорія: МУЗИКА."
    ],
    "МИСТЕЦТВО": [
        "Виставка сучасного мистецтва. МИСТЕЦТВО в деталях.",
        "Творчий майстер-клас. МИСТЕЦТВО та дизайн.",
        "Арт-перформанс."
    ],
    "БІЗНЕС": [
        "Бізнес-форум та нетворкінг. Тема: БІЗНЕС.",
        "Зустріч підприємців. БІЗНЕС та інвестиції.",
        "Семінар з маркетингу."
    ],
    "НАУКА": [
        "Наукова лекція. Категорія: НАУКА.",
        "Презентація відкриттів. Світ науки (НАУКА).",
        "Зустріч з вченими."
    ],
    "ОСВІТА": [
        "Освітній інтенсив. ОСВІТА для всіх.",
        "Відкрита лекція та воркшоп. Формат: ОНЛАЙН.",
        "Тренінг soft skills."
    ],
    "РОЗВАГИ": [
        "Весела вечірка. РОЗВАГИ та ІГРИ.",
        "Фестиваль розваг. Відпочинок та РОЗВАГИ.",
        "Тематичний вечір. Настільні ІГРИ."
    ],
    "СПОРТ": [
        "Спортивне тренування. СПОРТ та здоров'я.",
        "Марафон та біг. Активний РАНОК.",
        "Заняття йогою. Категорія: СПОРТ."
    ],
    "ПОЛІТИКА": [
        "Політична дискусія. Тема: ПОЛІТИКА.",
        "Дебати та новини (ПОЛІТИКА).",
        "Громадська зустріч."
    ],
    "ЛЕКЦІЯ": [
        "Інформативна ЛЕКЦІЯ від експерта.",
        "Публічний виступ. Цікава ЛЕКЦІЯ.",
        "Презентація. Формат: ЛЕКЦІЯ."
    ]
}

def create_enriched_description(row, category):
    templates = DESCRIPTION_TEMPLATES.get(category, ["Цікава подія."])
    base_text = random.choice(templates)
    
    details = []
    
    # Додаємо трохи "солі" - рандомні теги, щоб модель їх вивчила
    # Це гарантує, що слова ОНЛАЙН, ОФЛАЙН, ІГРИ будуть у словнику
    extra_tags = ["ОНЛАЙН", "ОФЛАЙН", "ВЕЧІР", "РАНОК", "ІГРИ", "КІНО"]
    if random.random() > 0.3: # 70% шанс додати додатковий тег
        base_text += f" Додатково: {random.choice(extra_tags)}."

    topic = str(row.get('Topic', ''))
    if topic: details.append(f"Original Topic: {topic}.")
    
    location = str(row.get('Location', ''))
    if location: details.append(f"Location: {location}.")
    
    return f"{base_text} {' '.join(details)}"

def filter_and_enrich():
    print(f" Читаємо {FILENAME}...")
    try:
        # Читаємо Location!
        df = pd.read_csv(FILENAME, encoding='latin1', 
                         usecols=['Event Type', 'Topic', 'Location']) 
    except Exception as e:
        print(f" Помилка: {e}")
        return

    df = df.fillna('')
    df['Search_Text'] = df['Event Type'].astype(str) + " " + df['Topic'].astype(str)
    
    all_selected = []
    used_indices = set()
    
    print("\n Генерація та збагачення...")
    
    for category, keywords in TARGET_CATEGORIES.items():
        pattern = '|'.join(keywords)
        matches = df[
            df['Search_Text'].str.contains(pattern, case=False, na=False) & 
            ~df.index.isin(used_indices)
        ]
        
        sample_size = min(LIMIT_PER_CATEGORY, len(matches))
        if sample_size > 0:
            selected = matches.sample(n=sample_size, random_state=42)
            selected = selected.copy()
            selected['our_category'] = category
            selected['description'] = selected.apply(
                lambda row: create_enriched_description(row, category), axis=1
            )
            all_selected.append(selected)
            used_indices.update(selected.index)
            print(f"   -> {category}: {len(selected)} подій")

    if not all_selected:
        print(" Нічого не знайдено.")
        return

    final_df = pd.concat(all_selected, ignore_index=True)
    
    # Зберігаємо без Location, як ви просили, але опис вже містить її
    save_df = final_df[['our_category', 'description', 'Topic', 'Event Type']]
    save_df.columns = ['category', 'description', 'original_topic', 'original_type']
    save_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    
    print(f"\n Готово! Збережено у '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    filter_and_enrich()