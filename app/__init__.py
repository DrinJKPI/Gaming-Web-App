from flask import Flask
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

    from .oauth import init_oauth
    init_oauth(app)

    # Initialize MongoDB
    from .mongodb import init_mongodb
    init_mongodb(app)

    # Register the main Blueprint
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Register the API Blueprint
    from .api_routes import api_bp
    app.register_blueprint(api_bp)

    # Register the Auth Blueprint
    from .auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    # Debug: Print all registered routes
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.rule}")
    print()

    return app