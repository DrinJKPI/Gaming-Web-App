import os
from dotenv import load_dotenv
load_dotenv()

print(f"DEBUG MYSQL_HOST: {os.getenv('MYSQL_HOST')}")
print(f"DEBUG MYSQL_PORT: {os.getenv('MYSQL_PORT')}")
print(f"DEBUG MYSQL_USER: {os.getenv('MYSQL_USER')}")
print(f"DEBUG DB URI: {os.getenv('MYSQL_DATABASE')}")

class Config:
    SECRET_KEY = "dev-secret-key-change-later"
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
        f"?ssl_disabled=true"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_URI = os.getenv("MONGO_URI")