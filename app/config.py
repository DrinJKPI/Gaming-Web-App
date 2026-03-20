import os
from dotenv import load_dotenv
load_dotenv()

print(f"DEBUG MYSQL_HOST: {os.getenv('MYSQL_HOST')}")
print(f"DEBUG MYSQL_PORT: {os.getenv('MYSQL_PORT')}")
print(f"DEBUG MYSQL_USER: {os.getenv('MYSQL_USER')}")
print(f"DEBUG DB URI: {os.getenv('MYSQL_DATABASE')}")
print(f"DEBUG STEAM KEY FROM ENV: {os.getenv('STEAM_API_KEY')}")

class Config:
    SECRET_KEY = "dev-secret-key-change-later"
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
        f"?ssl_disabled=true"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_URI = os.getenv("MONGO_URI")

    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://127.0.0.1:5000/auth/google/callback')

    STEAM_API_KEY = os.getenv('STEAM_API_KEY')