import sys
import os
import pickle

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ml_recommendations import get_recommendations

def test():
    # Load metadata to see what titles we have
    try:
        with open('games_metadata.pkl', 'rb') as f:
            df = pickle.load(f)
            print(f"Titles in metadata: {df['title'].head(5).tolist()}")
            
            if not df.empty:
                test_title = df['title'].iloc[0]
                print(f"Testing recommendations for: {test_title}")
                recs = get_recommendations(test_title)
                print(f"Recommendations: {recs}")
            else:
                print("Metadata is empty!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
