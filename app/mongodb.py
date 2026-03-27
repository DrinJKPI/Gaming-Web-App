from pymongo import MongoClient
from app.config import Config

# Initialize MongoDB client
mongo_client = None
mongo_db = None


def init_mongodb(app):
    """Initialize MongoDB connection"""
    global mongo_client, mongo_db

    if not Config.MONGO_URI:
        print("MONGO_URI not set; MongoDB disabled")
        return None

    try:
        mongo_client = MongoClient(Config.MONGO_URI)
        mongo_db = mongo_client['gaming_store']

        # Test connection
        mongo_client.admin.command('ping')
        print("MongoDB connected successfully")

        return mongo_db
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return None


def get_mongodb():
    """Get MongoDB database instance"""
    return mongo_db