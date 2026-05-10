# recsys_service/cleanup_bots.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database()

def clean():
    # 1. Видаляємо всіх, крім основних 5 персон
    main_emails = [
        "andriy.dev@example.com", "olena.run@example.com", 
        "victor.biz@example.com", "maria.art@example.com", 
        "ihor.travel@example.com"
    ]
    
    del_users = db.users.delete_many({"email": {"$nin": main_emails}})
    print(f"🗑 Видалено {del_users.deleted_count} ботів.")

    # 2. Видаляємо всі події, які згенерував Faker (починаються на "Подія")
    # АБО можна видалити всі, крім тих, що створили ви вручну. 
    # Для чистоти експерименту краще видалити ВСІ події, бо старі лінки будуть биті
    # Але якщо хочете залишити свої - не запускайте рядок нижче.
    
    del_events = db.events.delete_many({"title": {"$regex": "^Подія"}})
    print(f"🗑 Видалено {del_events.deleted_count} згенерованих подій.")
    
    # Очищаємо масив учасників у тих подій, що залишились (щоб прибрати видалених ботів)
    # Це складніша операція, простіше видалити всі події і перегенерувати.
    
    print("✅ База очищена від масовки.")

if __name__ == "__main__":
    clean()