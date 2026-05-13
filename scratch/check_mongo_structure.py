import sys
import os
sys.path.append(os.getcwd())
from app import create_app
from app.mongodb import get_mongodb

app = create_app()
with app.app_context():
    db = get_mongodb()
    if db is not None:
        game = db.games.find_one()
        print("Keys in MongoDB game document:")
        if game:
            for key in game.keys():
                print(f"- {key}: {type(game[key])}")
            if 'stores' in game:
                print("\nStores info:")
                print(game['stores'])
        else:
            print("No games found in MongoDB.")
    else:
        print("Failed to connect to MongoDB.")
