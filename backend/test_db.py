import os
from database import engine
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        # Try to connect to the engine
        with engine.connect() as connection:
            print("Successfully connected to AWS RDS PostgreSQL database")
    except Exception as e:
        print("Failed to connect to the database. Error:")
        print(e)

if __name__ == "__main__":
    test_connection()
