from app.ml_recommendations import get_recommendations as get_ml_recs
from cloud_functions.generate_recommendations import get_score_based_recommendations
from app.services import get_user_library
from app.models import Game
from app.game_metadata_service import get_game_by_id_from_mongodb

class HybridRecommender:
    # In-memory cache to store recommendations per user
    # Format: {user_id: [list of game dicts]}
    _CACHE = {}

    @classmethod
    def clear_cache(cls, user_id=None):
        """Clears the recommendation cache for a specific user or all users."""
        if user_id:
            cls._CACHE.pop(user_id, None)
            print(f"Cache cleared for user {user_id}")
        else:
            cls._CACHE.clear()
            print("All recommendation caches cleared")

    @classmethod
    def get_homepage_recommendations(cls, user_id, limit=4):
        """
        Generates high-quality recommendations using a blend of 
        ML-based similarity and Rule-based scoring. Uses a cache for performance.
        """
        # Check cache first
        if user_id in cls._CACHE:
            print(f"Returning cached recommendations for user {user_id}")
            return cls._CACHE[user_id]

        try:
            user_library = get_user_library(user_id)
            if not user_library:
                return []

            owned_ids = [entry["game_id"] for entry in user_library]
            
            # --- 1. ML-Based Extraction (Multi-Seed) ---
            # Get similarity results for the last 3 games added to library
            ml_candidates = []
            recent_games = user_library[-3:] if len(user_library) >= 3 else user_library
            
            for entry in reversed(recent_games):
                g = Game.query.get(entry["game_id"])
                if g:
                    # Get 3 similar games per seed
                    similar_titles = get_ml_recs(g.title, num_recommendations=3)
                    for title in similar_titles:
                        # Find the game object
                        match = Game.query.filter_by(title=title).first()
                        if match and match.game_id not in owned_ids:
                            ml_candidates.append(match)

            # --- 2. Rule-Based Extraction ---
            rule_candidates = get_score_based_recommendations(user_library, limit=limit*2)
            
            # --- 3. Merging and De-duplication ---
            unique_recommendations = []
            seen_ids = set(owned_ids)

            # High priority: ML candidates
            for g in ml_candidates:
                if g.game_id not in seen_ids:
                    unique_recommendations.append(g)
                    seen_ids.add(g.game_id)
            
            # Fill the rest with Rule-based candidates
            for g_dict in rule_candidates:
                g_id = g_dict.get('mysql_game_id')
                if g_id and g_id not in seen_ids:
                    # Fetch from MySQL to get full object
                    g_obj = Game.query.get(g_id)
                    if g_obj:
                        unique_recommendations.append(g_obj)
                        seen_ids.add(g_id)
            
            # --- 4. Hydration (Metadata from MongoDB) ---
            final_recs = []
            for game_obj in unique_recommendations[:limit]:
                metadata = get_game_by_id_from_mongodb(game_obj.game_id)
                final_recs.append({
                    "game_id": game_obj.game_id,
                    "title": game_obj.title,
                    "price": float(game_obj.price) if game_obj.price else 0.0,
                    "background_image": metadata.get("background_image") if metadata else None,
                    "description": metadata.get("description") if metadata else "No description available."
                })
            
            # Store in cache
            cls._CACHE[user_id] = final_recs
            
            return final_recs

        except Exception as e:
            print(f"Hybrid Recommender Error: {e}")
            import traceback
            traceback.print_exc()
            return []
