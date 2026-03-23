from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from werkzeug.middleware.proxy_fix import ProxyFix
from app.config import Config
from app.oauth import init_oauth
from app.mongodb import init_mongodb
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Initialize extensions (Keep these outside create_app)
db = SQLAlchemy()
bcrypt = Bcrypt() # <--- Initialize it here

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

    # Initialize Extensions
    db.init_app(app)
    bcrypt.init_app(app) # <--- Add this line
    init_oauth(app)
    init_mongodb(app)

    # Register Blueprints
    # Note: Using local imports inside the function helps prevent circular errors
    from app.routes import main_bp
    from app.auth_routes import auth_bp
    from app.api_routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()

    return app