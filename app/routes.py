from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services import get_user_by_email, create_user, check_password, get_user_by_username

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("home.html")


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
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        full_name = request.form.get("full_name")

        # Check if user already exists
        if get_user_by_email(email):
            return render_template("register.html", error="Email already registered"), 400

        if get_user_by_username(username):
            return render_template("register.html", error="Username already taken"), 400

        # Create new user
        try:
            create_user(username, email, password, full_name)
            return redirect(url_for("main.login"))
        except Exception as e:
            print(f"Error creating user: {e}")
            return render_template("register.html", error="Registration failed"), 500

    return render_template("register.html")


@main_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.home"))