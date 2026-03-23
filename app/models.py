from datetime import datetime
from app import db
from flask_login import UserMixin

# ---- User Model ----

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)      # Nullable for OAuth users
    password_hash = db.Column(db.String(255), nullable=True)           # Nullable for OAuth users
    full_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships — cascade delete removes sessions/library entries when user is deleted
    sessions = db.relationship('UserSession', backref='user', lazy=True, cascade='all, delete-orphan')
    library = db.relationship('UserLibrary', backref='user', lazy=True, cascade='all, delete-orphan')


# ---- Game Model ----

class Game(db.Model):
    __tablename__ = 'games'

    game_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    platform = db.Column(db.String(50))
    price = db.Column(db.Numeric(6, 2))
    release_date = db.Column(db.Date)  # Add this line

    # Cascade delete removes library entries when a game is deleted
    library_entries = db.relationship('UserLibrary', backref='game', lazy=True, cascade='all, delete-orphan')


# ---- User Session Model ----

class UserSession(db.Model):
    __tablename__ = 'user_sessions'

    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    token = db.Column(db.String(500), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)


# ---- User Library Model ----

class UserLibrary(db.Model):
    __tablename__ = 'user_library'

    library_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), nullable=False)
    platform = db.Column(db.String(50))

    def get_id(self):
        return str(self.user_id)


# ---- OAuth Account Model ----

class OAuthAccount(db.Model):
    __tablename__ = 'oauth_accounts'

    oauth_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    provider = db.Column(db.Enum('google', 'steam', 'epic'), nullable=False)
    provider_account_id = db.Column(db.String(255), nullable=False)          # Unique ID from the provider
    access_token = db.Column(db.String(500))
    token_expiry = db.Column(db.DateTime)
    linked_at = db.Column(db.DateTime)

    # Backref allows user.oauth_accounts to list all linked providers
    user = db.relationship('User', backref='oauth_accounts')