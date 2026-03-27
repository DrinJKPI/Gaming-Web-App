import os
from dotenv import load_dotenv

load_dotenv()

def _normalize_database_url(url: str) -> str:
    """Ensure SQLAlchemy MySQL driver prefix for URIs like mysql:// from some hosts."""
    if url.startswith("mysql://") and "+pymysql" not in url.split("://", 1)[0]:
        return "mysql+pymysql://" + url[len("mysql://") :]
    return url


class Config:
    # General
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-before-deployment')

    # MySQL: full URL (e.g. Cloud SQL, Secret Manager) or discrete MYSQL_* vars
    _database_url = os.getenv("DATABASE_URL")
    if _database_url:
        SQLALCHEMY_DATABASE_URI = _normalize_database_url(_database_url)
    else:
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