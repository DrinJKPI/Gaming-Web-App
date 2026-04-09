from app import create_app, db
from app.models import Game

app = create_app()

with app.app_context():
    print("Rebuilding database schema...")
    db.drop_all()  # This deletes all tables (games, user_library, etc.)
    db.create_all()  # This creates them fresh with the 'release_date' column

    # Curated games data (5 from each year: 2025, 2024, 2023)
    games_data = [
        {"title": "Black Myth: Wukong", "platform": "PC", "price": 59.99, "tags": "Action RPG RPG Fantasy Souls-like Souls-like"},
        {"title": "Monster Hunter Wilds", "platform": "PC", "price": 69.99, "tags": "Action RPG RPG Monster-Hunter Fantasy Co-op"},
        {"title": "Crimson Desert", "platform": "PC", "price": 59.99, "tags": "Action RPG RPG Open-World Fantasy"},
        {"title": "Dragon Age: The Veilguard", "platform": "PC", "price": 59.99, "tags": "RPG RPG Fantasy Story-Driven Choice-Matters"},
        {"title": "Baldur's Gate 3", "platform": "PC", "price": 59.99, "tags": "RPG RPG Turn-Based Fantasy Tactical"},
        {"title": "Elden Ring: Shadow of the Erdtree", "platform": "PC", "price": 39.99, "tags": "Action RPG RPG Souls-like Open-World Fantasy"},
        {"title": "Death Stranding 2: On The Beach", "platform": "PlayStation", "price": 69.99, "tags": "Action Adventure Sci-Fi Cinematic Exploration"},

        # FIGHTING (Traditional, Arena, and Platform)
        {"title": "Street Fighter 6", "platform": "PC", "price": 59.99, "tags": "Fighting Fighting 2D Competitive Arcade"},
        {"title": "Mortal Kombat 1", "platform": "PC", "price": 69.99, "tags": "Fighting Fighting 2D Brutal Competitive"},
        {"title": "Tekken 8", "platform": "PC", "price": 69.99, "tags": "Fighting Fighting 3D Competitive Martial-Arts"},
        {"title": "Guilty Gear -Strive-", "platform": "PC", "price": 39.99, "tags": "Fighting Fighting 2D Anime Stylized"},
        {"title": "Dragon Ball FighterZ", "platform": "PC", "price": 59.99, "tags": "Fighting Fighting 2D Anime Team-Based"},
        {"title": "Naruto: Ultimate Ninja Storm 4", "platform": "PC", "price": 49.99, "tags": "Arena-Brawler Arena-Brawler Fighting Fighting Anime 3D"},
        {"title": "Dragon Ball: Sparking! ZERO", "platform": "PC", "price": 69.99, "tags": "Arena-Brawler Arena-Brawler Fighting Fighting Anime 3D"},
        {"title": "Super Smash Bros. Ultimate", "platform": "Switch", "price": 59.99, "tags": "Platform-Fighter Fighting Platformer Nintendo Multiplayer"},
        {"title": "2XKO", "platform": "PC", "price": 0.00, "tags": "Fighting Fighting 2D Tag-Team Competitive Assist-Based"},

        # SPORTS & RACING
        {"title": "EA Sports FC 26", "platform": "PC", "price": 69.99, "tags": "Sports Sports Football Soccer Simulation Competitive"},
        {"title": "NBA 2K26", "platform": "PC", "price": 69.99, "tags": "Sports Sports Basketball Simulation Competitive"},
        {"title": "Gran Turismo 7", "platform": "PlayStation", "price": 69.99, "tags": "Sports Sports Racing Simulation Realistic Car-Culture"},
        {"title": "Madden NFL 26", "platform": "Xbox", "price": 69.99, "tags": "Sports Sports Football Simulation Competitive"},

        # PLATFORMERS & METROIDVANIAS
        {"title": "Hollow Knight", "platform": "PC", "price": 14.99, "tags": "Metroidvania Metroidvania Metroidvania Indie Souls-like 2D"},
        {"title": "Hollow Knight: Silksong", "platform": "PC", "price": 29.99, "tags": "Metroidvania Metroidvania Metroidvania Indie 2D Difficult"},
        {"title": "Ori and the Will of the Wisps", "platform": "PC", "price": 29.99, "tags": "Metroidvania Metroidvania 2D Beautiful Indie"},
        {"title": "Celeste", "platform": "PC", "price": 19.99, "tags": "Precision-Platformer Precision-Platformer Platformer 2D Indie Difficult"},
        {"title": "Pizza Tower", "platform": "PC", "price": 19.99, "tags": "High-Speed-Platformer Platformer 2D Indie Stylized"},

        # ROGUELIKES
        {"title": "Slay the Spire 2", "platform": "PC", "price": 24.99, "tags": "Roguelike Roguelike Deckbuilder Card-Game Indie"},
        {"title": "Hades II", "platform": "PC", "price": 29.99, "tags": "Roguelike Roguelike Action Action-RPG Indie Mythological"}
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