from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from .config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)

    # Register the Blueprint
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Debug: Print all registered routes
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.rule}")
    print()

    # Error handlers to see what's actually happening
    @app.errorhandler(404)
    def not_found_error(error):
        print(f"404 Error caught: {error}")
        return "404 - Page Not Found", 404

    @app.errorhandler(500)
    def internal_error(error):
        print(f"500 Error caught: {error}")
        return "500 - Internal Server Error", 500

    return app