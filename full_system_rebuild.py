import os
import time
from app import create_app, db
from app.models import Game
from app.game_metadata_service import save_game_to_mongodb
from enrich_game_metadata import fetch_game_metadata  # Uses your existing RAWG logic

app = create_app()

# Your recompleted master dictionary
games_data = [
    {"title": "Ghost of Yotei", "platform": "PlayStation", "price": 69.99, "release_date": "2025-10-01",
     "tags": "Action Adventure Open-World Samurai Stealth"},
    {"title": "Monster Hunter Wilds", "platform": "PC", "price": 69.99, "release_date": "2025-02-28",
     "tags": "Action RPG RPG Monster-Hunter Fantasy Co-op"},
    {"title": "Crimson Desert", "platform": "PC", "price": 59.99, "release_date": "2025-05-01",
     "tags": "Action RPG RPG Open-World Fantasy"},
    {"title": "Death Stranding 2: On The Beach", "platform": "PlayStation", "price": 69.99,
     "release_date": "2025-01-01", "tags": "Action Adventure Sci-Fi Cinematic Exploration"},
    {"title": "Slay the Spire 2", "platform": "PC", "price": 24.99, "release_date": "2025-03-01",
     "tags": "Roguelike Roguelike Deckbuilder Card-Game Indie"},
    {"title": "2XKO", "platform": "PC", "price": 0.00, "release_date": "2025-06-01",
     "tags": "Fighting Fighting 2D Tag-Team Competitive Assist-Based"},
    {"title": "Hollow Knight: Silksong", "platform": "PC", "price": 29.99, "release_date": "2025-12-31",
     "tags": "Metroidvania Metroidvania Metroidvania Indie 2D Difficult"},
    {"title": "Black Myth: Wukong", "platform": "PC", "price": 59.99, "release_date": "2024-08-20",
     "tags": "Action RPG RPG Fantasy Souls-like Souls-like"},
    {"title": "Assassin's Creed Shadows", "platform": "PC", "price": 69.99, "release_date": "2024-11-15",
     "tags": "Action RPG Stealth Open-World Ninja History"},
    {"title": "Helldivers 2", "platform": "PC", "price": 39.99, "release_date": "2024-02-08",
     "tags": "Action Shooter Third-Person Co-op Sci-Fi"},
    {"title": "Silent Hill 2 Remake", "platform": "PC", "price": 69.99, "release_date": "2024-10-08",
     "tags": "Horror Survival-Horror Psychological-Horror Remake"},
    {"title": "Dragon Ball: Sparking! ZERO", "platform": "PC", "price": 69.99, "release_date": "2024-10-11",
     "tags": "Arena-Brawler Arena-Brawler Fighting Fighting Anime 3D"},
    {"title": "Dragon Age: The Veilguard", "platform": "PC", "price": 59.99, "release_date": "2024-10-31",
     "tags": "RPG RPG Fantasy Story-Driven Choice-Matters"},
    {"title": "Hades II", "platform": "PC", "price": 29.99, "release_date": "2024-05-06",
     "tags": "Roguelike Roguelike Action Action-RPG Indie Mythological"},
    {"title": "Tekken 8", "platform": "PC", "price": 69.99, "release_date": "2024-01-26",
     "tags": "Fighting Fighting 3D Competitive Martial-Arts"},
    {"title": "Baldur's Gate 3", "platform": "PC", "price": 59.99, "release_date": "2023-08-03",
     "tags": "RPG RPG Turn-Based Fantasy Tactical"},
    {"title": "The Legend of Zelda: Tears of the Kingdom", "platform": "Switch", "price": 69.99,
     "release_date": "2023-05-12", "tags": "Adventure Open-World Fantasy Exploration Nintendo"},
    {"title": "Hogwarts Legacy", "platform": "PC", "price": 59.99, "release_date": "2023-02-10",
     "tags": "Action-RPG Fantasy Open-World Magic Wizarding-World"},
    {"title": "Resident Evil 4 Remake", "platform": "PC", "price": 59.99, "release_date": "2023-03-24",
     "tags": "Action Horror Survival-Horror Remake Third-Person"},
    {"title": "Alan Wake 2", "platform": "PC", "price": 49.99, "release_date": "2023-10-27",
     "tags": "Horror Survival-Horror Psychological-Horror Supernatural Cinematic"},
    {"title": "Street Fighter 6", "platform": "PC", "price": 59.99, "release_date": "2023-06-02",
     "tags": "Fighting Fighting 2D Competitive Arcade"},
    {"title": "Mortal Kombat 1", "platform": "PC", "price": 69.99, "release_date": "2023-09-14",
     "tags": "Fighting Fighting 2D Brutal Competitive"},
    {"title": "Pizza Tower", "platform": "PC", "price": 19.99, "release_date": "2023-01-26",
     "tags": "High-Speed-Platformer Platformer 2D Indie Stylized"},
    {"title": "EA Sports FC 26", "platform": "PC", "price": 69.99, "release_date": "2025-09-22",
     "tags": "Sports Sports Football Soccer Simulation Competitive"},
    {"title": "NBA 2K26", "platform": "PC", "price": 69.99, "release_date": "2025-09-05",
     "tags": "Sports Sports Basketball Simulation Competitive"},
    {"title": "Madden NFL 26", "platform": "Xbox", "price": 69.99, "release_date": "2025-08-15",
     "tags": "Sports Sports Football Simulation Competitive"},
    {"title": "Gran Turismo 7", "platform": "PlayStation", "price": 69.99, "release_date": "2022-03-04",
     "tags": "Sports Sports Racing Simulation Realistic Car-Culture"},
    {"title": "Hollow Knight", "platform": "PC", "price": 14.99, "release_date": "2017-02-24",
     "tags": "Metroidvania Metroidvania Metroidvania Indie Souls-like 2D"},
    {"title": "Ori and the Will of the Wisps", "platform": "PC", "price": 29.99, "release_date": "2020-03-11",
     "tags": "Metroidvania Metroidvania 2D Beautiful Indie"},
    {"title": "Celeste", "platform": "PC", "price": 19.99, "release_date": "2018-01-25",
     "tags": "Precision-Platformer Precision-Platformer Platformer 2D Indie Difficult"},
    {"title": "Guilty Gear -Strive-", "platform": "PC", "price": 39.99, "release_date": "2021-06-11",
     "tags": "Fighting Fighting 2D Anime Stylized"},
    {"title": "Dragon Ball FighterZ", "platform": "PC", "price": 59.99, "release_date": "2018-01-26",
     "tags": "Fighting Fighting 2D Anime Team-Based"},
    {"title": "Naruto: Ultimate Ninja Storm 4", "platform": "PC", "price": 49.99, "release_date": "2016-02-04",
     "tags": "Arena-Brawler Arena-Brawler Fighting Fighting Anime 3D"},
    {"title": "Super Smash Bros. Ultimate", "platform": "Switch", "price": 59.99, "release_date": "2018-12-07",
     "tags": "Platform-Fighter Fighting Platformer Nintendo Multiplayer"},
    {"title": "Elden Ring: Shadow of the Erdtree", "platform": "PC", "price": 39.99, "release_date": "2024-06-21",
     "tags": "Action RPG RPG Souls-like Open-World Fantasy"}
]


def rebuild_all():
    with app.app_context():
        print("Syncing database schema with Railway...")
        # This drops the old tables and creates them with the NEW columns
        db.drop_all()
        db.create_all()
        print("MySQL tables recreated successfully.")

        print(f"Starting rebuild for {len(games_data)} games...")

        for i, game_info in enumerate(games_data, 1):
            print(f"[{i}/{len(games_data)}] Processing: {game_info['title']}...")

            # 1. Save to MySQL
            new_game = Game(
                title=game_info['title'],
                platform=game_info['platform'],
                price=game_info['price'],
                release_date=game_info['release_date']
            )
            db.session.add(new_game)
            db.session.flush()  # Gets the game_id from MySQL immediately

            # 2. Fetch Metadata from RAWG
            rawg_meta = fetch_game_metadata(game_info['title'])
            if not rawg_meta:
                rawg_meta = {}

            # 3. Prepare MongoDB document
            # Combine your dictionary data + RAWG metadata
            mongo_data = {
                'mysql_game_id': new_game.game_id,
                'title': new_game.title,
                'platform': new_game.platform,
                'price': new_game.price,
                'release_date': new_game.release_date,
                'tags': game_info['tags'],  # Essential for ML
                'genres': rawg_meta.get('genres', []),
                'description': rawg_meta.get('description', ''),
                'background_image': rawg_meta.get('background_image'),
                'rating': rawg_meta.get('rating'),
                'metacritic_score': rawg_meta.get('metacritic_score'),
                'developer': rawg_meta.get('developer', []),
                'publisher': rawg_meta.get('publisher', []),
                'playtime': rawg_meta.get('playtime')
            }

            # 4. Save to MongoDB
            save_game_to_mongodb(mongo_data)

            # 5. Update MySQL with image/rating (optional but recommended for visual consistency)
            new_game.background_image = rawg_meta.get('background_image')
            new_game.rating = rawg_meta.get('rating')

            # Sleep to prevent RAWG rate-limiting
            time.sleep(0.5)

        db.session.commit()
        print("\n" + "=" * 30)
        print("REBUILD COMPLETE!")
        print("=" * 30)


if __name__ == "__main__":
    rebuild_all()