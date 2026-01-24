import os

from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = "dev-secret-key-change-later"

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:12345678@localhost/gaming_store"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MONGO_URI = os.getenv("MONGO_URI")