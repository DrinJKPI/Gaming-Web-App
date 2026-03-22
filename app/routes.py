from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services import get_user_by_email, create_user, check_password, get_user_by_username, get_all_games, add_game_to_library, get_game_by_id, get_user_library, remove_game_from_library
from app.game_metadata_service import get_all_games_from_mongodb, get_game_by_id_from_mongodb
from cloud_functions.generate_recommendations import generate_recommendations
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    """Home page — loads all games from MongoDB and checks user library ownership"""
    games = get_all_games_from_mongodb()

    # If user is logged in, get their library to check which games they already own
    user_library_game_ids = []
    if "user_id" in session:
        user_id = session["user_id"]
        user_library = get_user_library(user_id)
        user_library_game_ids = [entry.game_id for entry in user_library]

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
    """Display the user's game library, enriched with MongoDB metadata"""
    # Redirect to library page without data if user is not logged in
    if "user_id" not in session:
        return render_template("library.html")

    user_id = session["user_id"]

    # Get core library entries from MySQL
    library_entries = get_user_library(user_id)

    # Enrich each entry with additional metadata from MongoDB
    enriched_library = []
    for entry in library_entries:
        mongo_game = get_game_by_id_from_mongodb(entry.game_id)
        if mongo_game:
            entry.game.background_image = mongo_game.get('background_image')
            entry.game.genres = mongo_game.get('genres', [])
            entry.game.rating = mongo_game.get('rating')
        enriched_library.append(entry)

    return render_template("library.html", library_games=enriched_library)


@main_bp.route("/add-to-library/<int:game_id>", methods=["POST"])
def add_to_library(game_id):
    """Add a game to the logged-in user's library"""
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user_id = session["user_id"]

    try:
        # Verify the game exists in MongoDB before adding
        game = get_game_by_id_from_mongodb(game_id)
        if not game:
            return "Game not found", 404

        # Add to library using the MySQL game_id
        add_game_to_library(user_id, game_id, game.get('platform'))
        return redirect(url_for("main.home"))

    except Exception as e:
        logger.error(f"Error adding game {game_id} to library: {e}")
        return "Error adding game to library", 500


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
    """Display AI-generated game recommendations for the logged-in user"""
    if "user_id" not in session:
        return render_template("recommendations.html")

    user_id = session["user_id"]

    # Get user's library to exclude already owned games from recommendations
    user_library = get_user_library(user_id)
    user_library_game_ids = [entry.game_id for entry in user_library]

    # Generate personalised recommendations
    recommended_games = generate_recommendations(user_id, limit=5)

    return render_template(
        "recommendations.html",
        recommendations=recommended_games,
        user_library_game_ids=user_library_game_ids
    )