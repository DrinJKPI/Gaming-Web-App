"""
Cloud Function: Generate Game Recommendations
Input: user_id
Output: List of recommended games based on user's library
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.services import get_user_library
from app.game_metadata_service import get_all_games_from_mongodb, get_game_by_id_from_mongodb
from collections import Counter


def get_score_based_recommendations(user_library, limit=5):
    """Core logic to generate recommendations from library data"""
    try:
        if not user_library:
            return []

        # Get owned game IDs
        owned_game_ids = [entry["game_id"] for entry in user_library]

        # Fetch owned games from MongoDB to analyze preferences
        owned_games = []
        for game_id in owned_game_ids:
            game = get_game_by_id_from_mongodb(game_id)
            if game:
                owned_games.append(game)

        # Analyze user's genre preferences
        genre_counter = Counter()
        tag_counter = Counter()

        for game in owned_games:
            for genre in game.get('genres', []):
                genre_counter[genre] += 1
            for tag in game.get('tags', [])[:5]:
                tag_counter[tag] += 1

        top_genres = [genre for genre, _ in genre_counter.most_common(3)]
        top_tags = [tag for tag, _ in tag_counter.most_common(5)]

        all_games = get_all_games_from_mongodb()
        scored_recommendations = []

        for game in all_games:
            if game.get('mysql_game_id') in owned_game_ids:
                continue

            score = 0
            for genre in game.get('genres', []):
                if genre in top_genres:
                    score += 3
            for tag in game.get('tags', []):
                if tag in top_tags:
                    score += 1
            if game.get('rating'):
                score += game['rating']

            if score > 0:
                scored_recommendations.append({
                    'game': game,
                    'score': score
                })

        scored_recommendations.sort(key=lambda x: x['score'], reverse=True)
        return [rec['game'] for rec in scored_recommendations[:limit]]

    except Exception as e:
        print(f"Error in scoring logic: {e}")
        return []

def generate_recommendations(user_id, limit=5):
    """Backwards compatible wrapper for standalone use"""
    app = create_app()
    with app.app_context():
        user_library = get_user_library(user_id)
        return get_score_based_recommendations(user_library, limit)


# For testing locally
if __name__ == "__main__":
    # Test with a user ID
    test_user_id = 2  # Replace with your actual user ID
    recommendations = generate_recommendations(test_user_id)

    print("\n" + "=" * 60)
    print(f"RECOMMENDATIONS FOR USER {test_user_id}")
    print("=" * 60)

    for i, game in enumerate(recommendations, 1):
        print(f"\n{i}. {game['title']}")
        print(f"   Platform: {game['platform']}")
        print(f"   Price: ${game['price']}")
        print(f"   Genres: {', '.join(game.get('genres', []))}")
        print(f"   Rating: {game.get('rating', 'N/A')}")