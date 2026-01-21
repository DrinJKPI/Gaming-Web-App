from app import bcrypt, db
from app.models import User

users = {}


def hash_password(password: str) -> str:
    """Hash a password and return it as a string."""
    return bcrypt.generate_password_hash(password).decode('utf-8')


def check_password(password: str, hashed: str) -> bool:
    """Check if password matches the hashed version."""
    return bcrypt.check_password_hash(hashed, password)


def get_user_by_email(email: str):
    """Retrieve a user by email."""
    return User.query.filter_by(email=email).first()


def get_user_by_username(username: str):
    """Retrieve a user by username."""
    return User.query.filter_by(username=username).first()


def create_user(username: str, email: str, password: str, full_name: str = None):
    """Create a new user in the database."""
    password_hash = hash_password(password)

    new_user = User(
        username = username,
        email = email,
        password_hash = password_hash,
        full_name = full_name
    )

    db.session.add(new_user)
    db.session.commit()

    return new_user