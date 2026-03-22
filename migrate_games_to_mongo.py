from app import create_app, db
from app.models import Game
from app.game_metadata_service import save_game_to_mongodb
from datetime import date
import logging

# Utility script — run directly to migrate all games from MySQL to MongoDB
# Usage: python migrate_games_to_mongo.py

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


app = create_app()

with app.app_context():
    print("=" * 60)
    print("MIGRATING GAMES FROM MYSQL TO MONGODB")
    print("=" * 60)

    # Fetch all games from MySQL
    games = Game.query.all()
    print(f"\nFound {len(games)} games in MySQL database\n")

    success_count = 0
    failed_count = 0

    for game in games:
        print(f"Migrating: {game.title}...")

        # Prepare game data for MongoDB
        # mysql_game_id is kept as a reference back to the MySQL record
        game_data = {
            'mysql_game_id': game.game_id,  # Keep reference to MySQL ID
            'title': game.title,
            'platform': game.platform,
            'price': float(game.price) if game.price else 0.0,
            'release_date': game.release_date.isoformat() if game.release_date else None,

            # Extended metadata fields — populated later via external API enrichment
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

        # Attempt to save to MongoDB
        result = save_game_to_mongodb(game_data)

        if result:
            success_count += 1
            print(f"Success")
        else:
            failed_count += 1
            print(f"Failed")

    # Summary report
    logger.info("\n" + "=" * 60)
    logger.info("MIGRATION COMPLETE")
    logger.info(f"  Successful : {success_count}")
    logger.info(f"  Failed     : {failed_count}")
    logger.info(f"  Total      : {len(games)}")
    logger.info("=" * 60)