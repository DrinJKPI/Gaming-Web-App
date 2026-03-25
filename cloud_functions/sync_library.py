"""
Cloud Function: Sync User Library
Keeps MySQL and MongoDB in sync when users add/remove games
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.services import add_game_to_library, remove_game_from_library, get_user_library
from app.game_metadata_service import get_game_by_id_from_mongodb
from app.mongodb import get_mongodb
from datetime import datetime


def sync_library_action(user_id, game_id, action="add", platform=None):
    """
    Sync library action between MySQL and MongoDB

    Args:
        user_id: ID of the user
        game_id: ID of the game (MySQL game_id)
        action: "add" or "remove"
        platform: Game platform (optional)

    Returns:
        dict with success status and message
    """
    app = create_app()

    with app.app_context():
        try:
            if action == "add":
                # Add to MySQL user_library
                result = add_game_to_library(user_id, game_id, platform)

                if result:
                    # Update MongoDB with user activity
                    update_user_activity_in_mongo(user_id, game_id, "added")

                    return {
                        "success": True,
                        "message": f"Game {game_id} added to library",
                        "action": "add"
                    }
                else:
                    return {
                        "success": False,
                        "message": "Game already in library or add failed",
                        "action": "add"
                    }

            elif action == "remove":
                # Remove from MySQL user_library
                result = remove_game_from_library(user_id, game_id)

                if result:
                    # Update MongoDB with user activity
                    update_user_activity_in_mongo(user_id, game_id, "removed")

                    return {
                        "success": True,
                        "message": f"Game {game_id} removed from library",
                        "action": "remove"
                    }
                else:
                    return {
                        "success": False,
                        "message": "Game not in library or remove failed",
                        "action": "remove"
                    }
            else:
                return {
                    "success": False,
                    "message": f"Invalid action: {action}",
                    "action": action
                }

        except Exception as e:
            print(f"Error syncing library: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "action": action
            }


def update_user_activity_in_mongo(user_id, game_id, action):
    """
    Track user activity in MongoDB for analytics/recommendations
    """
    try:
        mongo_db = get_mongodb()
        if mongo_db is None:
            print("MongoDB not connected")
            return False

        collection = mongo_db['user_activity']

        activity = {
            'user_id': user_id,
            'game_id': game_id,
            'action': action,  # "added" or "removed"
            'timestamp': datetime.utcnow()
        }

        collection.insert_one(activity)
        print(f"Logged activity: User {user_id} {action} game {game_id}")
        return True

    except Exception as e:
        print(f"Error logging activity: {e}")
        return False


def get_library_summary(user_id):
    """
    Get a summary of user's library with enriched data from MongoDB
    """
    app = create_app()

    with app.app_context():
        try:
            # Get library from MySQL
            user_library = get_user_library(user_id)

            if not user_library:
                return {
                    "user_id": user_id,
                    "total_games": 0,
                    "games": []
                }

            # Enrich with MongoDB data
            enriched_games = []
            for entry in user_library:
                game = get_game_by_id_from_mongodb(entry["game_id"])
                if game:
                    enriched_games.append({
                        'title': game['title'],
                        'platform': game['platform'],
                        'price': game['price'],
                        'genres': game.get('genres', []),
                        'rating': game.get('rating')
                    })

            return {
                "user_id": user_id,
                "total_games": len(enriched_games),
                "games": enriched_games
            }

        except Exception as e:
            print(f"Error getting library summary: {e}")
            return {
                "user_id": user_id,
                "error": str(e)
            }


# For testing locally
if __name__ == "__main__":
    test_user_id = 2
    test_game_id = 48  # Change to an actual game ID

    print("=" * 60)
    print("TESTING LIBRARY SYNC")
    print("=" * 60)

    # Test adding a game
    print("\n1. Adding game to library...")
    result = sync_library_action(test_user_id, test_game_id, "add", "PC")
    print(f"   Result: {result}")

    # Get library summary
    print("\n2. Getting library summary...")
    summary = get_library_summary(test_user_id)
    print(f"   User {test_user_id} has {summary['total_games']} games")

    # Test removing the game
    print("\n3. Removing game from library...")
    result = sync_library_action(test_user_id, test_game_id, "remove")
    print(f"   Result: {result}")

    print("\n" + "=" * 60)