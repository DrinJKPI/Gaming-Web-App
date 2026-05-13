from app.ml_recommendations import get_recommendations as get_ml_recs
from cloud_functions.generate_recommendations import get_score_based_recommendations
from app.services import get_user_library
from app.models import Game
from app.game_metadata_service import get_games_by_ids_from_mongodb

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
            ml_titles = []
            recent_games = user_library[-3:] if len(user_library) >= 3 else user_library
            
            for entry in reversed(recent_games):
                # Use a title cache or fetch from DB efficiently
                seed_game = Game.query.get(entry["game_id"])
                if seed_game:
                    ml_titles.extend(get_ml_recs(seed_game.title, num_recommendations=3))

            # Fetch all ML candidate objects in one batch
            ml_candidates = Game.query.filter(
                Game.title.in_(ml_titles),
                ~Game.game_id.in_(owned_ids)
            ).all()

            # --- 2. Rule-Based Extraction ---
            rule_candidates = get_score_based_recommendations(user_library, limit=limit*2)
            
            # --- 3. Merging and De-duplication ---
            candidate_ids = []
            seen_ids = set(owned_ids)

            # High priority: ML candidates
            for g in ml_candidates:
                if g.game_id not in seen_ids:
                    candidate_ids.append(g.game_id)
                    seen_ids.add(g.game_id)
            
            # Fill with Rule-based candidates
            rule_ids = [r['mysql_game_id'] for r in rule_candidates if r.get('mysql_game_id') not in seen_ids]
            candidate_ids.extend(rule_ids[:limit])
            
            # --- 4. Batch Hydration (Metadata from MongoDB) ---
            target_ids = candidate_ids[:limit]
            all_metadata = get_games_by_ids_from_mongodb(target_ids)
            metadata_map = {m['mysql_game_id']: m for m in all_metadata}
            
            # Fetch MySQL objects for these final IDs in one batch
            final_game_objs = Game.query.filter(Game.game_id.in_(target_ids)).all()
            game_obj_map = {g.game_id: g for g in final_game_objs}

            final_recs = []
            for gid in target_ids:
                game_obj = game_obj_map.get(gid)
                metadata = metadata_map.get(gid)
                if game_obj:
                    final_recs.append({
                        "game_id": game_obj.game_id,
                        "title": game_obj.title,
                        "price": float(game_obj.price) if game_obj.price else 0.0,
                        "background_image": metadata.get("background_image") if metadata else None,
                        "description": metadata.get("description") if metadata else "No description available.",
                        "steam_url": metadata.get("steam_url") if metadata else None
                    })
            
            # Store in cache
            cls._CACHE[user_id] = final_recs
            return final_recs

        except Exception as e:
            print(f"Hybrid Recommender Error: {e}")
            import traceback
            traceback.print_exc()
            return []
