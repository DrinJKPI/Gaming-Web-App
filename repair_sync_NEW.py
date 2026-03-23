from app import create_app, db as mysql_db
from app.models import Game, UserLibrary

app = create_app()

# Use the data that matches your MongoDB IDs exactly
games_to_sync = [
    {"id": 46, "title": "Hollow Knight: Silksong", "platform": "PC", "price": 39.99},
    {"id": 47, "title": "Death Stranding 2: On The Beach", "platform": "PC", "price": 69.99},
    {"id": 48, "title": "Ghost of Yotei", "platform": "PlayStation", "price": 69.99},
    {"id": 49, "title": "Monster Hunter Wilds", "platform": "PC", "price": 59.99},
    {"id": 50, "title": "Assassin's Creed Shadows", "platform": "PC", "price": 69.99},
    {"id": 51, "title": "Black Myth: Wukong", "platform": "PC", "price": 59.99},
    {"id": 52, "title": "Helldivers 2", "platform": "PC", "price": 39.99},
    {"id": 53, "title": "Dragon Age: The Veilguard", "platform": "PC", "price": 59.99},
    {"id": 54, "title": "Tekken 8", "platform": "PC", "price": 69.99},
    {"id": 55, "title": "Silent Hill 2 Remake", "platform": "PC", "price": 69.99},
    {"id": 56, "title": "Baldur's Gate 3", "platform": "PC", "price": 59.99},
    {"id": 57, "title": "The Legend of Zelda: Tears of the Kingdom", "platform": "Switch", "price": 59.99},
    {"id": 58, "title": "Hogwarts Legacy", "platform": "PC", "price": 59.99},
    {"id": 59, "title": "Resident Evil 4 Remake", "platform": "PC", "price": 59.99},
    {"id": 60, "title": "Alan Wake 2", "platform": "PC", "price": 59.99}
]


def force_sync():
    with app.app_context():
        try:
            print("Step 1: Clearing User Library (to avoid FK errors)...")
            mysql_db.session.query(UserLibrary).delete()

            print("Step 2: Clearing Games table...")
            mysql_db.session.query(Game).delete()
            mysql_db.session.commit()

            print("Step 3: Injecting Games with IDs 46-60...")
            for g in games_to_sync:
                new_game = Game(
                    game_id=g['id'],
                    title=g['title'],
                    platform=g['platform'],
                    price=g['price']
                )
                mysql_db.session.add(new_game)

            mysql_db.session.commit()

            # This ensures the next game you add manually starts at 61
            mysql_db.session.execute(mysql_db.text("ALTER TABLE games AUTO_INCREMENT = 61"))
            mysql_db.session.commit()

            print("SUCCESS: MySQL IDs now match MongoDB IDs (46-60).")

        except Exception as e:
            mysql_db.session.rollback()
            print(f"FAILED: {e}")

if __name__ == "__main__":
    force_sync()