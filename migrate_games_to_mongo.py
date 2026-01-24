from app import create_app, db
from app.models import Game
from app.game_metadata_service import save_game_to_mongodb
from datetime import date

app = create_app()

with app.app_context():
    print("=" * 60)
    print("MIGRATING GAMES FROM MYSQL TO MONGODB")
    print("=" * 60)

    # Get all games from MySQL
    games = Game.query.all()
    print(f"\nFound {len(games)} games in MySQL database\n")

    success_count = 0
    failed_count = 0

    for game in games:
        print(f"Migrating: {game.title}...")

        # Prepare game data for MongoDB
        game_data = {
            'mysql_game_id': game.game_id,  # Keep reference to MySQL ID
            'title': game.title,
            'platform': game.platform,
            'price': float(game.price) if game.price else 0.0,
            'release_date': game.release_date.isoformat() if game.release_date else None,

            # Additional metadata fields (will be populated later via API)
            'description': '',
            'genres': [],
            'tags': [],
            'rating': None,
            'metacritic_score': None,
            'background_image': None,
            'developer': [],
            'publisher': [],
            'esrb_rating': None,
            'playtime': None
        }

        # Save to MongoDB
        result = save_game_to_mongodb(game_data)

        if result:
            success_count += 1
            print(f"Success")
        else:
            failed_count += 1
            print(f"Failed")

    print("\n" + "=" * 60)
    print(f"MIGRATION COMPLETE")
    print(f"Successful: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Total: {len(games)}")
    print("=" * 60)