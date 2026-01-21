from datetime import datetime
from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    sessions = db.relationship('UserSession', backref='user', lazy=True, cascade='all, delete-orphan')
    library = db.relationship('UserLibrary', backref='user', lazy=True, cascade='all, delete-orphan')

class Game(db.Model):
    __tablename__ = 'games'

    game_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    platform = db.Column(db.String(50))
    price = db.Column(db.Numeric(6, 2))

    # Relationships
    library_entries = db.relationship('UserLibrary', backref='game', lazy=True, cascade='all, delete-orphan')

class UserSession(db.Model):
    __tablename__ = 'user_sessions'

    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    token = db.Column(db.String(500), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

class UserLibrary(db.Model):
    __tablename__ = 'user_library'

    library_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.game_id'), nullable=False)
    platform = db.Column(db.String(50))

    def get_id(self):
        return str(self.user_id)