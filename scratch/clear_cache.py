import sys
import os
sys.path.append(os.getcwd())
from app.recommender_service import HybridRecommender

HybridRecommender.clear_cache()
print("Recommendation cache cleared.")
