import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 1. Database (Fixed)
    host = os.getenv('MYSQL_HOST', '127.0.0.1')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    database = os.getenv('MYSQL_DATABASE', 'railway')
    port = os.getenv('MYSQL_PORT', '3306')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?ssl_disabled=true"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 2. General
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-123')

    # 3. Google OAuth (Added placeholders to prevent KeyError)
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'placeholder-id')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', 'placeholder-secret')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://127.0.0.1:5000/auth/google/callback')

    # 4. Steam API (Added placeholder)
    STEAM_API_KEY = os.getenv('STEAM_API_KEY', 'placeholder-steam-key')

    # 5. MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/gaming_db')