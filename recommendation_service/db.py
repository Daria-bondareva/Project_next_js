from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

# Завантажуємо .env.local з кореня проекту
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env.local"))

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/testLogin")

# Підключення до MongoDB
client = MongoClient(MONGODB_URI)
db     = client.get_default_database()

users_col  = db["users"]
events_col = db["events"]

def get_user_interests(user_id: str) -> list[str]:
    """Повертає interests[] юзера за його ObjectId."""
    try:
        user = users_col.find_one(
            {"_id": ObjectId(user_id)},
            {"interests": 1}
        )
        if not user:
            return []
        return user.get("interests", [])
    except Exception as e:
        print(f"[db] get_user_interests error: {e}")
        return []

def get_all_events() -> list[dict]:
    """Повертає всі події з populate userId (username)."""
    try:
        pipeline = [
            {
                "$lookup": {
                    "from":         "users",
                    "localField":   "userId",
                    "foreignField": "_id",
                    "as":           "userInfo"
                }
            },
            {
                "$addFields": {
                    "userId": {
                        "$cond": {
                            "if":   {"$gt": [{"$size": "$userInfo"}, 0]},
                            "then": {
                                "_id":      {"$toString": {"$arrayElemAt": ["$userInfo._id", 0]}},
                                "username": {"$arrayElemAt": ["$userInfo.username", 0]}
                            },
                            "else": {"_id": "", "username": "Гість"}
                        }
                    }
                }
            },
            {"$sort": {"date": -1}},
            {"$limit": 200},
            {"$project": {"userInfo": 0}}
        ]
        events = list(events_col.aggregate(pipeline))
        return events
    except Exception as e:
        print(f"[db] get_all_events error: {e}")
        return []