from flask import Blueprint, render_template, request, redirect, url_for, session
from app.services import get_user_by_email, create_user, check_password, get_user_by_username, get_all_games, add_game_to_library, get_game_by_id, get_user_library, remove_game_from_library
from app.game_metadata_service import get_all_games_from_mongodb, get_game_by_id_from_mongodb

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    # Get all games from MongoDB
    games = get_all_games_from_mongodb()

    # If user is logged in, get their library to check which games they own
    user_library_game_ids = []
    if "user_id" in session:
        user_id = session["user_id"]
        user_library = get_user_library(user_id)
        user_library_game_ids = [entry.game_id for entry in user_library]

    return render_template("home.html", games=games, user_library_game_ids=user_library_game_ids)


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            email = request.form.get("email")
            password = request.form.get("password")

            print(f"Login attempt - Email: {email}")

            # Get user from database
            user = get_user_by_email(email)
            print(f"User found: {user}")

            if user:
                print(f"User is_active: {user.is_active}")
                print(f"Checking password...")
                password_match = check_password(password, user.password_hash)
                print(f"Password match: {password_match}")

                if user.is_active and password_match:
                    session["user_id"] = user.user_id
                    session["username"] = user.username
                    session["email"] = user.email
                    print("Login successful!")
                    return redirect(url_for("main.home"))

            print("Login failed - invalid credentials")
            return render_template("login.html", error="Invalid credentials"), 401

        except Exception as e:
            print(f"LOGIN ERROR: {e}")
            import traceback
            traceback.print_exc()
            return "Login error - check console", 500

    return render_template("login.html")


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            full_name = request.form.get("full_name")

            print(f"Registration attempt - Username: {username}, Email: {email}")
            print(f"Password: '{password}', Confirm: '{confirm_password}'")

            # Validate password confirmation
            if password != confirm_password:
                print("Password mismatch")
                return render_template("register.html", error="Passwords do not match"), 400

            # Validate password length
            if len(password) < 8:
                print("Password too short")
                return render_template("register.html", error="Password must be at least 8 characters"), 400

            # Check if user already exists
            print("Checking if user exists...")
            if get_user_by_email(email):
                print("Email already exists")
                return render_template("register.html", error="Email already registered"), 400

            if get_user_by_username(username):
                print("Username already exists")
                return render_template("register.html", error="Username already taken"), 400

            # Create new user
            print("Creating new user...")
            create_user(username, email, password, full_name)
            print("User created successfully")

            return redirect(url_for("main.login"))

        except Exception as e:
            print(f"REGISTRATION ERROR: {e}")
            import traceback
            traceback.print_exc()
            return render_template("register.html", error="Registration failed. Please try again."), 500

    return render_template("register.html")


@main_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.home"))


@main_bp.route("/library")
def library():
    # Check if user is logged in
    if "user_id" not in session:
        return render_template("library.html")

    user_id = session["user_id"]

    # Get user's library
    library_games = get_user_library(user_id)

    return render_template("library.html", library_games=library_games)


@main_bp.route("/add-to-library/<int:game_id>", methods=["POST"])
def add_to_library(game_id):
    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user_id = session["user_id"]

    try:
        # Get the game from MongoDB using mysql_game_id
        game = get_game_by_id_from_mongodb(game_id)
        if not game:
            return "Game not found", 404

        # Add game to user's library (using MySQL game_id)
        result = add_game_to_library(user_id, game_id, game.get('platform'))

        if result is None:
            # Game already in library
            print(f"Game {game_id} already in library for user {user_id}")
        else:
            print(f"Successfully added game {game_id} to library for user {user_id}")

        return redirect(url_for("main.home"))

    except Exception as e:
        print(f"Error adding game to library: {e}")
        import traceback
        traceback.print_exc()
        return "Error adding game to library", 500


@main_bp.route("/remove-from-library/<int:game_id>", methods=["POST"])
def remove_from_library(game_id):
    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user_id = session["user_id"]

    try:
        result = remove_game_from_library(user_id, game_id)

        if result:
            print(f"Successfully removed game {game_id} from library for user {user_id}")
        else:
            print(f"Game {game_id} not found in library for user {user_id}")

        return redirect(url_for("main.library"))

    except Exception as e:
        print(f"Error removing game from library: {e}")
        import traceback
        traceback.print_exc()
        return "Error removing game from library", 500