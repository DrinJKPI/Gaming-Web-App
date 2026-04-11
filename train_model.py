# train_model.py
import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from game_data import games_data # Clean import!

def train_unsupervised_model():
    df = pd.DataFrame(games_data)
    print(f"Training on {len(df)} games...")

    tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), sublinear_tf=True)
    tfidf_matrix = tfidf.fit_transform(df['tags'])
    similarity_matrix = cosine_similarity(tfidf_matrix)

    if not os.path.exists('app'):
        os.makedirs('app')

    with open('app/similarity_matrix.pkl', 'wb') as f:
        pickle.dump(similarity_matrix, f)
    with open('app/games_metadata.pkl', 'wb') as f:
        pickle.dump(df, f)

    print("Success! Model files saved in app/ folder.")

if __name__ == "__main__":
    train_unsupervised_model()