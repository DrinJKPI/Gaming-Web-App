import requests
import os
from dotenv import load_dotenv
from app import create_app
from app.game_metadata_service import get_all_games_from_mongodb, update_game_in_mongodb
import time

load_dotenv()
RAWG_API_KEY = os.getenv("RAWG_API_KEY")
RAWG_BASE_URL = "https://api.rawg.io/api"


def fetch_game_metadata(game_title):
    """Fetch metadata from RAWG API"""
    try:
        params = {
            "key": RAWG_API_KEY,
            "search": game_title,
            "page_size": 1
        }

        response = requests.get(f"{RAWG_BASE_URL}/games", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get('results'):
            print(f"No results found")
            return None

        game = data['results'][0]

        # Filter English-only tags (no Cyrillic characters)
        all_tags = game.get('tags', [])
        english_tags = [
            t['name'] for t in all_tags
            if t.get('language') == 'eng' or not any(ord(char) > 127 for char in t['name'])
        ][:10]

        # Extract metadata
        metadata = {
            "description": game.get('description_raw', '') or game.get('description', '')[
                :500] or "No description available.",
            "genres": [g['name'] for g in game.get('genres', [])][:5],
            "tags": english_tags,
            "rating": game.get('rating'),
            "metacritic_score": game.get('metacritic'),
            "background_image": game.get('background_image'),
            "developer": [d['name'] for d in game.get('developers', [])][:3],
            "publisher": [p['name'] for p in game.get('publishers', [])][:3],
            "esrb_rating": game.get('esrb_rating', {}).get('name') if game.get('esrb_rating') else None,
            "playtime": game.get('playtime')
        }

        return metadata

    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":  # <--- Add this line here
    app = create_app()
    with app.app_context():
        print("=" * 60)
        print("ENRICHING GAME METADATA FROM RAWG API")
        print("=" * 60)

        games = get_all_games_from_mongodb()
        print(f"\nFound {len(games)} games in MongoDB\n")

        success_count = 0

        for i, game in enumerate(games, 1):
            print(f"[{i}/{len(games)}] {game['title']}...")
            metadata = fetch_game_metadata(game['title'])

            if metadata:
                if update_game_in_mongodb(game['mysql_game_id'], metadata):
                    print(f"Updated with metadata")
                    success_count += 1
                else:
                    print(f"Failed to save")

            time.sleep(0.5)

        print("\n" + "=" * 60)
        print(f"ENRICHMENT COMPLETE")
        print(f"Enriched: {success_count}/{len(games)}")
        print("=" * 60)