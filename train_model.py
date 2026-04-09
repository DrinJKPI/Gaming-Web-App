# train_model.py (Root Level)
import pandas as pd
import pickle
from app import create_app, db
from app.models import Game
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def train_unsupervised_model():
    app = create_app()
    with app.app_context():
        # 1. Pull current data from the DB
        games = Game.query.all()
        data = [{"id": g.id, "title": g.title, "tags": g.tags} for g in games]
        df = pd.DataFrame(data)

        if df.empty:
            print("No games found in DB. Run seed_games.py first!")
            return

        print(f"Training on {len(df)} games...")

        # 2. The TF-IDF Logic (Your perfected settings)
        tfidf = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        tfidf_matrix = tfidf.fit_transform(df['tags'])

        # 3. The Similarity Matrix
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # 4. Save to files inside the app folder so recommendations.py can see them
        # We save the matrix and the dataframe (to map indices to IDs)
        with open('app/similarity_matrix.pkl', 'wb') as f:
            pickle.dump(similarity_matrix, f)

        with open('app/games_metadata.pkl', 'wb') as f:
            pickle.dump(df, f)

        print("Model trained and saved to app/ folder successfully.")


if __name__ == "__main__":
    train_unsupervised_model()