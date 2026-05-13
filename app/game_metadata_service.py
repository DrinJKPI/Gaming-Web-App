from app.mongodb import get_mongodb
from datetime import datetime
from bson import ObjectId


def save_game_to_mongodb(game_data):
    """Save a game to MongoDB"""
    try:
        db = get_mongodb()
        if db is None:  # Changed from "if not db"
            print("MongoDB not connected")
            return None

        collection = db['games']

        # Add timestamps
        game_data['created_at'] = datetime.utcnow()
        game_data['updated_at'] = datetime.utcnow()

        # Insert the game
        result = collection.insert_one(game_data)

        print(f"Saved game: {game_data.get('title')}")
        return str(result.inserted_id)

    except Exception as e:  # noqa
        print(f"Error saving game to MongoDB: {e}")
        return None


def get_all_games_from_mongodb():
    """Get all games from MongoDB"""
    try:
        db = get_mongodb()
        if db is None:  # Changed from "if not db"
            return []

        collection = db['games']
        games = list(collection.find())

        # Convert ObjectId to string for each game
        for game in games:
            game['_id'] = str(game['_id'])

        return games

    except Exception as e:  # noqa
        print(f"Error retrieving games: {e}")
        return []


def get_game_by_id_from_mongodb(game_id):
    """Get a single game by ID from MongoDB"""
    try:
        db = get_mongodb()
        if db is None:  # Changed from "if not db"
            return None

        collection = db['games']

        # Try to find by ObjectId first, then by mysql_game_id
        try:
            game = collection.find_one({'_id': ObjectId(game_id)})
        except:  # noqa
            game = collection.find_one({'mysql_game_id': int(game_id)})

        if game:
            game['_id'] = str(game['_id'])

        return game

    except Exception as e:  # noqa
        print(f"Error retrieving game: {e}")
        return None


def search_games_in_mongodb(query):
    """Search games by title in MongoDB"""
    try:
        db = get_mongodb()
        if db is None:  # Changed from "if not db"
            return []

        collection = db['games']

        # Case-insensitive search
        games = list(collection.find({
            'title': {'$regex': query, '$options': 'i'}
        }))

        # Convert ObjectId to string
        for game in games:
            game['_id'] = str(game['_id'])

        return games

    except Exception as e:  # noqa
        print(f"Error searching games: {e}")
        return []


def update_game_in_mongodb(game_id, update_data):
    """Update a game in MongoDB"""
    try:
        db = get_mongodb()
        if db is None:  # Changed from "if not db"
            return False

        collection = db['games']

        # Add updated timestamp
        update_data['updated_at'] = datetime.utcnow()

        # Try to update by ObjectId first, then by mysql_game_id
        try:
            result = collection.update_one(
                {'_id': ObjectId(game_id)},
                {'$set': update_data}
            )
        except:  # noqa
            result = collection.update_one(
                {'mysql_game_id': int(game_id)},
                {'$set': update_data}
            )

        return result.modified_count > 0

    except Exception as e:  # noqa
        print(f"Error updating game: {e}")
        return False


def get_games_by_ids_from_mongodb(game_ids):
    """Fetch multiple games from MongoDB in a single query"""
    try:
        db = get_mongodb()
        if db is None:
            return []

        collection = db['games']
        
        # Convert to int if they are mysql IDs
        int_ids = [int(gid) for gid in game_ids]
        
        games = list(collection.find({'mysql_game_id': {'$in': int_ids}}))

        for game in games:
            game['_id'] = str(game['_id'])

        return games

    except Exception as e:
        print(f"Error in batch retrieval: {e}")
        return []


def delete_game_from_mongodb(game_id):
    """Delete a game from MongoDB"""
    try:
        db = get_mongodb()
        if db is None:  # Changed from "if not db"
            return False

        collection = db['games']

        # Try to delete by ObjectId first, then by mysql_game_id
        try:
            result = collection.delete_one({'_id': ObjectId(game_id)})
        except:  # noqa
            result = collection.delete_one({'mysql_game_id': int(game_id)})

        return result.deleted_count > 0

    except Exception as e:  # noqa
        print(f"Error deleting game: {e}")
        return False