from app import create_app, db
from app.models import Game

app = create_app()

with app.app_context():
    # Clear existing games
    Game.query.delete()

    # Curated games data (5 from each year: 2025, 2024, 2023)
    games_data = [
        # 2025 Releases
        {"title": "Hollow Knight: Silksong", "platform": "PC", "price": 19.99},
        {"title": "Death Stranding 2: On The Beach", "platform": "PlayStation", "price": 69.99},
        {"title": "Ghost of Yotei", "platform": "PlayStation", "price": 69.99},
        {"title": "Monster Hunter Wilds", "platform": "PC", "price": 69.99},
        {"title": "Assassin's Creed Shadows", "platform": "PC", "price": 69.99},

        # 2024 Releases
        {"title": "Black Myth: Wukong", "platform": "PC", "price": 59.99},
        {"title": "Helldivers 2", "platform": "PC", "price": 39.99},
        {"title": "Dragon Age: The Veilguard", "platform": "PC", "price": 59.99},
        {"title": "Tekken 8", "platform": "PC", "price": 69.99},
        {"title": "Silent Hill 2 Remake", "platform": "PC", "price": 69.99},

        # 2023 Releases
        {"title": "Baldur's Gate 3", "platform": "PC", "price": 59.99},
        {"title": "The Legend of Zelda: Tears of the Kingdom", "platform": "Switch", "price": 59.99},
        {"title": "Hogwarts Legacy", "platform": "PC", "price": 59.99},
        {"title": "Resident Evil 4 Remake", "platform": "PC", "price": 59.99},
        {"title": "Alan Wake 2", "platform": "PC", "price": 59.99},
    ]

    # Add games to database
    for game_data in games_data:
        game = Game(**game_data)
        db.session.add(game)

    db.session.commit()

    # Verify
    all_games = Game.query.all()
    print(f"\nSuccessfully added {len(all_games)} games to the database:\n")
    for game in all_games:
        print(f"  - {game.title} ({game.platform}) - ${game.price}")