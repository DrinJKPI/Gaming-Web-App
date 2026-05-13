import sys
import os
sys.path.append(os.getcwd())
from app import create_app
from app.mongodb import get_mongodb

app = create_app()
with app.app_context():
    db = get_mongodb()
    if db is not None:
        games_with_url = list(db.games.find({"steam_url": {"$ne": None}}).limit(5))
        print(f"Found {len(games_with_url)} games with Steam URLs.")
        for g in games_with_url:
            print(f"- {g['title']}: {g['steam_url']}")
    else:
        print("Failed to connect to MongoDB.")
