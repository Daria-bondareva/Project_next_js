from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db import get_user_interests, get_all_events
from recommender import get_recommendations

app = FastAPI(title="Recommendation Service")

# CORS — дозволяємо Next.js звертатись до сервісу
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

def serialize_event(event: dict) -> dict:
    """Конвертує MongoDB документ у JSON-сумісний формат."""
    return {
        "_id":   str(event["_id"]),
        "title": event.get("title", ""),
        "date":  event["date"].isoformat() if hasattr(event.get("date"), "isoformat")
                 else str(event.get("date", "")),
        "tags":  event.get("tags", []),
        "userId": event.get("userId", {"_id": "", "username": "Гість"}),
    }

@app.get("/recommendations/{user_id}")
async def recommendations(user_id: str):
    try:
        # 1. Отримуємо interests юзера з MongoDB
        interests = get_user_interests(user_id)

        # 2. Отримуємо всі події з MongoDB
        events = get_all_events()
        if not events:
            return []

        # 3. Генеруємо рекомендації через ML моделі
        recommended = get_recommendations(
            user_interests=interests,
            user_id=user_id,
            mongo_events=events,
            top_n=10
        )

        # 4. Серіалізуємо і повертаємо
        return [serialize_event(e) for e in recommended]

    except Exception as e:
        print(f"[main] recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}