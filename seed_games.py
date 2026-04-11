# seed_games.py
from app import create_app, db
from app.models import Game
from game_data import games_data # Import from our new clean file

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    for game_data in games_data: # Use the clean list
        game = Game(**game_data)
        db.session.add(game)
    db.session.commit()