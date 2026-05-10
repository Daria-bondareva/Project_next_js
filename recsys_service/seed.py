# recsys_service/seed.py

from pymongo import MongoClient
from bson.objectid import ObjectId
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from faker import Faker

load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client.get_database()
fake = Faker()

CREATE_NEW_EVENTS = True 
DEFAULT_PASSWORD_HASH = "$2b$10$EpWsWB2rMNDpY/XX0.YVDOQe.e/j.M7G9Vd.i.t.y.u.i" 

ALL_TAGS = [
  'СПОРТ', 'IT', 'МУЗИКА', 'МИСТЕЦТВО', 'ЇЖА', 
  'ПОДОРОЖІ', 'НАУКА', 'БІЗНЕС', 'КІНО', 'ІГРИ',
  'ОНЛАЙН', 'ОФЛАЙН', 'РАНОК', 'ВЕЧІР', 'ЛЕКЦІЯ'
]

def seed_database():
    all_users_pool = []
    print(" ПОЧАТОК НАПОВНЕННЯ БАЗИ...")

    # 1. VIP КОРИСТУВАЧІ
    personas = [
        {"username": "Andriy", "email": "andriy.dev@example.com", "interests": ["IT", "ІГРИ", "ОНЛАЙН"]},
        {"username": "Olena", "email": "olena.run@example.com", "interests": ["СПОРТ", "РАНОК", "ЇЖА"]},
        {"username": "Victor", "email": "victor.biz@example.com", "interests": ["БІЗНЕС", "IT", "ЛЕКЦІЯ"]},
        {"username": "Maria", "email": "maria.art@example.com", "interests": ["МИСТЕЦТВО", "МУЗИКА", "ВЕЧІР"]},
        {"username": "Ihor", "email": "ihor.travel@example.com", "interests": ["ПОДОРОЖІ", "ОФЛАЙН", "СПОРТ"]}
    ]

    for p in personas:
        existing = db.users.find_one({"email": p["email"]})
        if existing:
            if not existing.get("interests"):
                db.users.update_one({"_id": existing["_id"]}, {"$set": {"interests": p["interests"]}})
            all_users_pool.append({"id": existing["_id"], "interests": existing.get("interests", p["interests"])})
        else:
            user = {
                "username": p["username"],
                "email": p["email"],
                "passwordHash": DEFAULT_PASSWORD_HASH,
                "interests": p["interests"]
            }
            res = db.users.insert_one(user)
            all_users_pool.append({"id": res.inserted_id, "interests": p["interests"]})

    # Додаємо інших існуючих
    others = db.users.find({"email": {"$nin": [p["email"] for p in personas]}})
    for u in others:
        interests = u.get("interests", [])
        if not interests:
            interests = random.sample(ALL_TAGS, k=3)
            db.users.update_one({"_id": u["_id"]}, {"$set": {"interests": interests}})
        all_users_pool.append({"id": u["_id"], "interests": interests})

    # 2. МАСОВКА
    NEW_BOTS_COUNT = 20
    print(f" Додаємо {NEW_BOTS_COUNT} ботів...")
    
    for _ in range(NEW_BOTS_COUNT):
        # 🛠 FIX #5: Надійний унікальний email
        unique_name = f"{fake.first_name()}_{random.randint(10000, 99999)}"
        safe_email = f"{unique_name}@example.com" # Ручна генерація, щоб уникнути дублів Faker
        
        interests = random.sample(ALL_TAGS, k=random.randint(2, 5))
        
        user = {
            "username": unique_name,
            "email": safe_email,
            "passwordHash": DEFAULT_PASSWORD_HASH,
            "interests": interests
        }
        try:
            res = db.users.insert_one(user)
            all_users_pool.append({"id": res.inserted_id, "interests": interests})
        except:
            print(f"!!! Пропущено дублікат юзера: {unique_name}")
            continue

    print(f" Всього юзерів: {len(all_users_pool)}")

    # 3. ПОДІЇ
    events_pool = []
    
    # Спочатку завантажимо існуючі
    existing_events = list(db.events.find())
    for e in existing_events:
        # Переконуємось, що є теги
        if not e.get("tags"):
            new_tags = random.sample(ALL_TAGS, k=2)
            db.events.update_one({"_id": e["_id"]}, {"$set": {"tags": new_tags}})
            e["tags"] = new_tags
        events_pool.append({"_id": e["_id"], "tags": e["tags"], "userId": e.get("userId")})

    if CREATE_NEW_EVENTS:
        print(" Перевірка шаблонів подій...")
        event_templates = [
            ("Воркшоп з Python", ["IT", "ОНЛАЙН", "ЛЕКЦІЯ"], "Інтенсивний воркшоп..."),
            ("Йога на даху", ["СПОРТ", "РАНОК", "ОФЛАЙН"], "Зустрічаємо схід сонця..."),
            ("Кіберспортивний марафон", ["ІГРИ", "IT", "ВЕЧІР"], "Турнір з CS:GO..."),
            ("Вино та Живопис", ["МУЗИКА", "ВЕЧІР", "МИСТЕЦТВО"], "Релакс-вечір..."),
            ("Стартап Пітчинг", ["БІЗНЕС", "ЛЕКЦІЯ", "ОНЛАЙН"], "Презентація ідей..."),
            ("Кемпінг у Карпатах", ["ПОДОРОЖІ", "ОФЛАЙН", "СПОРТ"], "Похід з наметами..."),
            ("Майстер-клас з суші", ["ЇЖА", "ОФЛАЙН", "ВЕЧІР"], "Готуємо роли..."),
            ("Фотовиставка", ["МИСТЕЦТВО", "ОФЛАЙН", "РАНОК"], "Сучасне фотомистецтво...")
        ]
        
        for tmpl in event_templates:
            #  FIX #4: Перевірка на дублікати за назвою
            title = tmpl[0]
            existing_event = db.events.find_one({"title": title})
            
            if not existing_event:
                author = random.choice(all_users_pool)
                event = {
                    "title": title,
                    "description": tmpl[2],
                    "date": datetime.now() + timedelta(days=random.randint(1, 30)),
                    "userId": author["id"],
                    "tags": tmpl[1],
                    "participants": []
                }
                res = db.events.insert_one(event)
                events_pool.append({"_id": res.inserted_id, "tags": tmpl[1], "userId": author["id"]})
            else:
                # Якщо вже є, просто додаємо в пул для кліків
                pass 

    print(f" Всього подій: {len(events_pool)}")

    # 4. ВЗАЄМОДІЯ
    print(" Імітація кліків...")
    count = 0
    for user in all_users_pool:
        num_actions = random.randint(3, 8)
        
        for _ in range(num_actions):
            is_logical = random.random() > 0.1 # 70% логіки
            chosen = None
            
            if is_logical:
                matches = [e for e in events_pool if set(e["tags"]) & set(user["interests"]) and str(e["userId"]) != str(user["id"])]
                if matches: chosen = random.choice(matches)
            
            if not chosen:
                candidates = [e for e in events_pool if str(e["userId"]) != str(user["id"])]
                if candidates: chosen = random.choice(candidates)
            
            if chosen:
                db.events.update_one(
                    {"_id": chosen["_id"]},
                    {"$addToSet": {"participants": user["id"]}}
                )
                count += 1

    print(f" Додано {count} кліків.")

if __name__ == "__main__":
    seed_database()