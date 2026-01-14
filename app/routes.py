from flask import Blueprint, render_template, request, redirect, url_for, session
from app.services import users, hash_password, check_password

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("home.html")

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users.get(email)
        if user and check_password(password, user["password"]):
            session["user"] = email
            return redirect(url_for("main.home"))

        return "Invalid credentials", 401

    return render_template("login.html")

@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in users:
            return "User already exists", 400

        users[email] = {
            "password": hash_password(password)
        }

        return redirect(url_for("main.login"))

    return render_template("register.html")

@main_bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("main.home"))