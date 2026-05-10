# recsys_service/fix_database.py

from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Налаштування
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client.get_database()

def fix_integrity():
    print("🚑 ПОЧАТОК ВІДНОВЛЕННЯ ЦІЛІСНОСТІ БАЗИ...")

    # 1. Отримуємо список ID всіх живих користувачів
    valid_users = list(db.users.find({}, {"_id": 1}))
    # Зберігаємо як набір рядків для швидкого пошуку
    valid_user_ids = set([str(u["_id"]) for u in valid_users])
    
    print(f"✅ Живих користувачів у базі: {len(valid_user_ids)}")

    # 2. ВИДАЛЕННЯ ПОДІЙ-СИРІТ (Авторів яких не існує)
    all_events = list(db.events.find({}, {"_id": 1, "userId": 1}))
    deleted_events_count = 0
    
    for event in all_events:
        author_id = str(event.get("userId"))
        if author_id not in valid_user_ids:
            db.events.delete_one({"_id": event["_id"]})
            deleted_events_count += 1
            
    print(f"🗑 Видалено подій неіснуючих авторів: {deleted_events_count}")

    # 3. ЧИСТКА СПИСКІВ УЧАСНИКІВ (Видалення мертвих душ)
    # Нам треба пройтись по всіх подіях, що залишились, і почистити масив participants
    
    events_to_clean = db.events.find({})
    cleaned_participants_count = 0
    
    for event in events_to_clean:
        original_participants = event.get("participants", [])
        
        # Залишаємо тільки тих, хто є у списку valid_user_ids
        # (Перевіряємо як рядки, щоб уникнути плутанини типів)
        valid_participants = [
            p for p in original_participants 
            if str(p) in valid_user_ids
        ]
        
        # Якщо список змінився - оновлюємо базу
        if len(original_participants) != len(valid_participants):
            removed_count = len(original_participants) - len(valid_participants)
            cleaned_participants_count += removed_count
            
            db.events.update_one(
                {"_id": event["_id"]},
                {"$set": {"participants": valid_participants}}
            )

    print(f"👻 Вигнано 'привидів' (видалених юзерів) з учасників: {cleaned_participants_count}")
    print("✨ БАЗА ДАНИХ ТЕПЕР ЧИСТА І ВАЛІДНА!")

if __name__ == "__main__":
    fix_integrity()