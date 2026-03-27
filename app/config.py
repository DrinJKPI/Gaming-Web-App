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
        _mu = os.getenv("MYSQL_USER")
        _mp = os.getenv("MYSQL_PASSWORD")
        _mh = os.getenv("MYSQL_HOST")
        _mport = os.getenv("MYSQL_PORT", "3306")
        _mdb = os.getenv("MYSQL_DATABASE")
        _missing = [
            n
            for n, v in (
                ("MYSQL_USER", _mu),
                ("MYSQL_PASSWORD", _mp),
                ("MYSQL_HOST", _mh),
                ("MYSQL_DATABASE", _mdb),
            )
            if not v
        ]
        if _missing:
            raise RuntimeError(
                "Database env not set. Either set DATABASE_URL, or set all of: "
                "MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE (and optionally MYSQL_PORT, default 3306). "
                "With Docker: docker run --env-file .env ..."
            )
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{_mu}:{_mp}@{_mh}:{_mport}/{_mdb}?ssl_disabled=true"
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