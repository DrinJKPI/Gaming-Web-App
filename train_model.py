import pandas as pd
import pickle
import os
from app import create_app
from app.mongodb import get_mongodb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = create_app()


def train_model():
    with app.app_context():
        print("MongoDB connected successfully")
        print("Fetching fresh data from MongoDB...")

        # 1. Connect using your specific helper function
        db = get_mongodb()
        if db is None:
            print("Error: Could not connect to MongoDB. Check your config.")
            return

        # 2. Pull games from the 'games' collection
        games = list(db.games.find())

        if not games:
            print("Error: MongoDB 'games' collection is empty. Run full_system_rebuild.py first!")
            return

        # 3. Load into DataFrame
        df = pd.DataFrame(games)
        print(f"Training model on {len(df)} games...")

        # 4. Create the 'Metadata Soup'
        # Convert lists to strings and handle NaN values
        df['tags'] = df['tags'].fillna('').astype(str)
        df['genres_str'] = df['genres'].apply(lambda x: ' '.join(x) if isinstance(x, list) else '').astype(str)

        # Combine and apply lowercase using the Pandas .str accessor
        df['metadata_soup'] = (df['tags'] + ' ' + df['genres_str']).str.lower()

        # 5. Vectorization (TF-IDF)
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['metadata_soup'])

        # 6. Calculate Similarity Matrix
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

        # 7. Save to the Root Directory
        # This matches the BASE_DIR / '..' path in your ml_recommendations.py
        try:
            with open('games_metadata.pkl', 'wb') as f:
                pickle.dump(df, f)
            with open('similarity_matrix.pkl', 'wb') as f:
                pickle.dump(cosine_sim, f)
            print("\n" + "=" * 30)
            print("SUCCESS: Model trained and files saved!")
            print("=" * 30)
        except Exception as e:
            print(f"Error saving files: {e}")


if __name__ == "__main__":
    train_model()