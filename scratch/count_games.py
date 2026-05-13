import sys
import os
sys.path.append(os.getcwd())
from app import create_app
from app.mongodb import get_mongodb

app = create_app()
with app.app_context():
    db = get_mongodb()
    if db is not None:
        count = db.games.count_documents({})
        print(f"Total games in MongoDB: {count}")
    else:
        print("Failed to connect to MongoDB.")
