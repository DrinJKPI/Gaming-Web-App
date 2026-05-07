import pickle
import pandas as pd

def check_pkl():
    try:
        with open('games_metadata.pkl', 'rb') as f:
            df = pickle.load(f)
            print(f"Total games in PKL: {len(df)}")
            print("First 10 games:")
            print(df[['title', 'mysql_game_id']].head(10))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_pkl()
