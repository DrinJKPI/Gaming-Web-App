import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # General
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-before-deployment')

    # MySQL (Railway)
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
        f"?ssl_disabled=true"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MongoDB Atlas
    MONGO_URI = os.getenv('MONGO_URI')

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://127.0.0.1:5000/auth/google/callback')

    # Steam
    STEAM_API_KEY = os.getenv('STEAM_API_KEY')