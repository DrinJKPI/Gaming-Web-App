from app import bcrypt, db
from app.models import User, Game, UserLibrary
from datetime import datetime

users = {}


def hash_password(password: str) -> str:
    """Hash a password and return it as a string."""
    return bcrypt.generate_password_hash(password).decode('utf-8')


def check_password(password: str, hashed: str) -> bool:
    """Check if password matches the hashed version."""
    print(f"check_password called")
    print(f"  Password type: {type(password)}, value: {password}")
    print(f"  Hashed type: {type(hashed)}, value: {hashed[:20]}...")
    print(f"  Hashed length: {len(hashed)}")

    try:
        result = bcrypt.check_password_hash(hashed, password)
        print(f"  Result: {result}")
        return result
    except Exception as e:
        print(f"  Exception in check_password: {e}")
        import traceback
        traceback.print_exc()
        raise

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

def get_all_games():
    """Retrieve all games."""
    return Game.query.all()


def get_game_by_id(game_id: int):
    """Retrieve a game by ID."""
    return Game.query.get(game_id)


def add_game_to_library(user_id: int, game_id: int, platform: str = None):
    """Add a game to user's library."""
    # Check if already in library
    existing = UserLibrary.query.filter_by(user_id=user_id, game_id=game_id).first()
    if existing:
        return None

    library_entry = UserLibrary(
        user_id=user_id,
        game_id=game_id,
        platform=platform
    )

    db.session.add(library_entry)
    db.session.commit()

    return library_entry


def get_user_library(user_id: int):
    """Get all games in user's library."""
    return UserLibrary.query.filter_by(user_id=user_id).all()


def remove_game_from_library(user_id: int, game_id: int):
    """Remove a game from user's library."""
    library_entry = UserLibrary.query.filter_by(user_id=user_id, game_id=game_id).first()

    if not library_entry:
        return False

    db.session.delete(library_entry)
    db.session.commit()
    return True

def get_or_create_oauth_user(provider, provider_account_id, email, username, access_token):
    from app.models import User, OAuthAccount
    from app import db

    # Check if oauth account already exists
    oauth_account = OAuthAccount.query.filter_by(
        provider=provider,
        provider_account_id=provider_account_id
    ).first()

    if oauth_account:
        # Update access token
        oauth_account.access_token = access_token
        db.session.commit()
        return oauth_account.user

    # Check if user with this email already exists
    user = None
    if email:
        user = User.query.filter_by(email=email).first()

    # Create new user if doesn't exist
    if not user:
        # Generate unique username if taken
        base_username = username.replace(' ', '').lower()[:50]
        final_username = base_username
        counter = 1
        while User.query.filter_by(username=final_username).first():
            final_username = f"{base_username}{counter}"
            counter += 1

        user = User(
            username=final_username,
            email=email,
            password_hash=None,
            created_at=datetime.utcnow(),
            is_active=1
        )
        db.session.add(user)
        db.session.flush()

    # Create oauth account link
    oauth_account = OAuthAccount(
        user_id=user.user_id,
        provider=provider,
        provider_account_id=provider_account_id,
        access_token=access_token,
        linked_at=datetime.utcnow()
    )
    db.session.add(oauth_account)
    db.session.commit()

    return user