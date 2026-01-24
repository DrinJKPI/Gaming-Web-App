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


def generate_recommendations(user_id, limit=5):
    """
    Generate game recommendations based on user's library

    Args:
        user_id: ID of the user
        limit: Number of recommendations to return

    Returns:
        List of recommended games
    """
    app = create_app()

    with app.app_context():
        try:
            # Get user's library
            user_library = get_user_library(user_id)

            if not user_library:
                print(f"No library found for user {user_id}")
                return []

            # Get owned game IDs
            owned_game_ids = [entry.game_id for entry in user_library]

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
                for tag in game.get('tags', [])[:5]:  # Top 5 tags
                    tag_counter[tag] += 1

            # Get top preferred genres and tags
            top_genres = [genre for genre, _ in genre_counter.most_common(3)]
            top_tags = [tag for tag, _ in tag_counter.most_common(5)]

            print(f"User preferences - Genres: {top_genres}, Tags: {top_tags}")

            # Get all games
            all_games = get_all_games_from_mongodb()

            # Score and filter recommendations
            recommendations = []

            for game in all_games:
                # Skip games already in library
                if game.get('mysql_game_id') in owned_game_ids:
                    continue

                score = 0

                # Score based on genre match
                for genre in game.get('genres', []):
                    if genre in top_genres:
                        score += 3

                # Score based on tag match
                for tag in game.get('tags', []):
                    if tag in top_tags:
                        score += 1

                # Bonus for high ratings
                if game.get('rating'):
                    score += game['rating']

                if score > 0:
                    recommendations.append({
                        'game': game,
                        'score': score
                    })

            # Sort by score and return top N
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            top_recommendations = [rec['game'] for rec in recommendations[:limit]]

            print(f"Generated {len(top_recommendations)} recommendations")
            return top_recommendations

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            import traceback
            traceback.print_exc()
            return []


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