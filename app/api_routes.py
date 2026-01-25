"""
REST API Routes
Provides external access to game and user library data
"""

from flask import Blueprint, jsonify, request
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.game_metadata_service import (
    get_all_games_from_mongodb,
    get_game_by_id_from_mongodb,
    search_games_in_mongodb
)
from app.services import get_user_library
from cloud_functions.generate_recommendations import generate_recommendations
from cloud_functions.sync_library import get_library_summary

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/games", methods=["GET"])
def get_games():
    """Get all games - Returns JSON list of all games"""
    try:
        games = get_all_games_from_mongodb()

        # Simplify game data for API response
        simplified_games = []
        for game in games:
            simplified_games.append({
                'id': game.get('mysql_game_id'),
                'title': game.get('title'),
                'platform': game.get('platform'),
                'price': game.get('price'),
                'release_date': game.get('release_date'),
                'genres': game.get('genres', []),
                'rating': game.get('rating'),
                'image': game.get('background_image')
            })

        return jsonify({
            'success': True,
            'count': len(simplified_games),
            'games': simplified_games
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route("/games/<int:game_id>", methods=["GET"])
def get_game(game_id):
    """Get a single game by ID - Returns detailed game information"""
    try:
        game = get_game_by_id_from_mongodb(game_id)

        if not game:
            return jsonify({
                'success': False,
                'error': 'Game not found'
            }), 404

        # Return full game data
        game_data = {
            'id': game.get('mysql_game_id'),
            'title': game.get('title'),
            'platform': game.get('platform'),
            'price': game.get('price'),
            'release_date': game.get('release_date'),
            'description': game.get('description'),
            'genres': game.get('genres', []),
            'tags': game.get('tags', []),
            'rating': game.get('rating'),
            'metacritic_score': game.get('metacritic_score'),
            'image': game.get('background_image'),
            'developer': game.get('developer', []),
            'publisher': game.get('publisher', []),
            'esrb_rating': game.get('esrb_rating'),
            'playtime': game.get('playtime')
        }

        return jsonify({
            'success': True,
            'game': game_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route("/games/search", methods=["GET"])
def search_games():
    """Search games by title - Query parameter: ?q=search_term"""
    try:
        query = request.args.get('q', '')

        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query parameter "q" is required'
            }), 400

        games = search_games_in_mongodb(query)

        simplified_games = []
        for game in games:
            simplified_games.append({
                'id': game.get('mysql_game_id'),
                'title': game.get('title'),
                'platform': game.get('platform'),
                'price': game.get('price'),
                'genres': game.get('genres', []),
                'rating': game.get('rating'),
                'image': game.get('background_image')
            })

        return jsonify({
            'success': True,
            'query': query,
            'count': len(simplified_games),
            'games': simplified_games
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route("/recommendations/<int:user_id>", methods=["GET"])
def get_recommendations(user_id):
    """Get game recommendations for a user - Query parameter: ?limit=5"""
    try:
        limit = request.args.get('limit', 5, type=int)
        recommendations = generate_recommendations(user_id, limit)

        simplified_recs = []
        for game in recommendations:
            simplified_recs.append({
                'id': game.get('mysql_game_id'),
                'title': game.get('title'),
                'platform': game.get('platform'),
                'price': game.get('price'),
                'genres': game.get('genres', []),
                'rating': game.get('rating'),
                'image': game.get('background_image')
            })

        return jsonify({
            'success': True,
            'user_id': user_id,
            'count': len(simplified_recs),
            'recommendations': simplified_recs
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route("/library/<int:user_id>", methods=["GET"])
def get_library(user_id):
    """Get user's game library - Returns list of games in user's library"""
    try:
        summary = get_library_summary(user_id)

        return jsonify({
            'success': True,
            'user_id': user_id,
            'total_games': summary.get('total_games', 0),
            'games': summary.get('games', [])
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500