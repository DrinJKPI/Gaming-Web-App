from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services import get_user_by_email, create_user, check_password, get_user_by_username, get_all_games, add_game_to_library, get_game_by_id, get_user_library, remove_game_from_library
from app.game_metadata_service import get_all_games_from_mongodb, get_game_by_id_from_mongodb
from cloud_functions.generate_recommendations import generate_recommendations
from app.ml_recommendations import get_recommendations
from app.services import get_user_library
from app.models import Game # Import the SQLAlchemy Game model
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    games = get_all_games_from_mongodb()

    user_library_game_ids = []
    if "user_id" in session:
        user_id = session["user_id"]
        user_library = get_user_library(user_id)
        # Ensure we are grabbing the IDs correctly regardless of format
        for entry in user_library:
            if isinstance(entry, dict):
                user_library_game_ids.append(entry.get('game_id'))
            else:
                user_library_game_ids.append(entry.game_id)

    return render_template("home.html", games=games, user_library_game_ids=user_library_game_ids)


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login — validates credentials and sets session variables"""
    if request.method == "POST":
        try:
            email = request.form.get("email")
            password = request.form.get("password")

            # Look up user by email
            user = get_user_by_email(email)

            if user and user.is_active and check_password(password, user.password_hash):
                # Set session variables on successful login
                session["user_id"] = user.user_id
                session["username"] = user.username
                session["email"] = user.email
                return redirect(url_for("main.home"))

            return render_template("login.html", error="Invalid credentials"), 401

        except Exception as e:
            logger.error(f"Login error: {e}")
            return render_template("login.html", error="Login failed. Please try again."), 500

    return render_template("login.html")


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration — validates input and creates a new user account"""
    if request.method == "POST":
        try:
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            full_name = request.form.get("full_name")

            # Validate password confirmation
            if password != confirm_password:
                return render_template("register.html", error="Passwords do not match"), 400

            # Validate password length
            if len(password) < 8:
                return render_template("register.html", error="Password must be at least 8 characters"), 400

            # Check for existing email or username
            if get_user_by_email(email):
                return render_template("register.html", error="Email already registered"), 400

            if get_user_by_username(username):
                return render_template("register.html", error="Username already taken"), 400

            # Create the new user account
            create_user(username, email, password, full_name)
            return redirect(url_for("main.login"))

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return render_template("register.html", error="Registration failed. Please try again."), 500

    return render_template("register.html")


@main_bp.route("/logout")
def logout():
    """Clear the user session and redirect to home"""
    session.clear()
    return redirect(url_for("main.home"))


@main_bp.route("/library")
def library():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user_id = session["user_id"]
    try:
        user_entries = get_user_library(user_id)
        game_ids = [entry["game_id"] for entry in user_entries if "game_id" in entry]

        # Use game_id instead of id here
        library_games = Game.query.filter(Game.game_id.in_(game_ids)).all() if game_ids else []
    except Exception as e:
        print(f"Library fetch error: {e}")
        library_games = []

    return render_template("library.html", library_games=library_games)


@main_bp.route("/add-to-library/<int:game_id>", methods=["POST"])
def add_to_library(game_id):
    print(f"DEBUG: Button clicked for Game ID: {game_id}")  # 1. Did the click reach Python?

    if "user_id" not in session:
        print("DEBUG: No user in session")  # 2. Is the user logged in?
        return redirect(url_for("main.login"))

    user_id = session["user_id"]
    game = Game.query.get(game_id)

    if game:
        success = add_game_to_library(user_id, game_id, game.platform)
        if success:
            print(f"DEBUG: Successfully added to DB")  # 3. Did the service work?
        else:
            print(f"DEBUG: Service failed to write to DB")

    return redirect(url_for("main.home"))


@main_bp.route("/remove-from-library/<int:game_id>", methods=["POST"])
def remove_from_library(game_id):
    """Remove a game from the logged-in user's library"""
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user_id = session["user_id"]

    try:
        remove_game_from_library(user_id, game_id)
        return redirect(url_for("main.library"))

    except Exception as e:
        logger.error(f"Error removing game {game_id} from library: {e}")
        return "Error removing game from library", 500


@main_bp.route("/recommendations")
def recommendations():
    # 1. Session check
    if "user_id" not in session:
        return render_template("recommendations.html", recommendations=[], user_library_game_ids=[])

    user_id = session["user_id"]
    recommended_games = []
    user_library_game_ids = []

    try:
        # 2. Get Library
        user_library = get_user_library(user_id)
        user_library_game_ids = [entry["game_id"] for entry in user_library]

        if user_library:
            last_game_id = user_library[-1]["game_id"]
            seed_game = Game.query.get(last_game_id)

            if seed_game:
                # 3. Get Recommendations
                similar_titles = get_recommendations(seed_game.title)

                # 4. Fetch from MySQL
                recommended_games = Game.query.filter(
                    Game.title.in_(similar_titles),
                    ~Game.game_id.in_(user_library_game_ids)
                ).all()

                # 5. ATTACH METADATA (The critical part)
                for game in recommended_games:
                    # Initialize attributes with defaults so Jinja doesn't crash
                    game.background_image = None
                    game.description = "No description available."

                    # Try to fill them from Mongo
                    metadata = get_game_metadata_from_mongodb(game.game_id)
                    if metadata:
                        game.background_image = metadata.get('background_image')
                        game.description = metadata.get('description', "No description available.")

    except Exception as e:
        # Use a print or logger to see EXACTLY what's failing in your console
        print(f"DEBUG: Recommendation Error -> {e}")

    return render_template(
        "recommendations.html",
        recommendations=recommended_games,
        user_library_game_ids=user_library_game_ids
    )

@main_bp.route('/debug-count')
def debug_count():
    from app.models import Game
    count = Game.query.count()
    return f"Database has {count} games."