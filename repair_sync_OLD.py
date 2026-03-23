from app import create_app, db as mysql_db
from app.models import Game, UserLibrary
from app.mongodb import init_mongodb, get_mongodb
from datetime import datetime

app = create_app()


def repair_database():
    with app.app_context():
        # 1. IMPORTANT: Initialize the connection first
        init_mongodb(app)
        mongo_db = get_mongodb()

        # 2. Fix the "Truth Value" error by checking against None
        if mongo_db is None:
            print("Could not connect to MongoDB.")
            return

        print("Step 1: Clearing MySQL tables to reset IDs...")
        try:
            # Clear library first because it depends on games
            mysql_db.session.query(UserLibrary).delete()
            mysql_db.session.query(Game).delete()
            mysql_db.session.commit()
        except Exception as e:
            mysql_db.session.rollback()
            print(f"Error clearing tables: {e}")
            return

        print("Step 2: Re-importing games from MongoDB...")
        # Access the collection - adjust 'games' if your collection name is different
        mongo_games = mongo_db.games.find({})

        added_count = 0
        for m_game in mongo_games:
            title = m_game.get('title')
            if not title:
                continue

            new_game = Game(
                title=title,
                platform=m_game.get('platform', 'PC'),
                price=m_game.get('price', 0.0),
                release_date=datetime.utcnow().date()
            )
            mysql_db.session.add(new_game)
            added_count += 1

        mysql_db.session.commit()
        print(f"Step 3: Database Synced! Added {added_count} games.")


if __name__ == "__main__":
    repair_database()