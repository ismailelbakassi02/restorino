from app import create_app
from models import db, User, Review, MenuItem, MenuItemReview, ReviewImage, MenuItemReviewImage
from config import Config
import sqlite3
import os

# This script will update the database schema to include the new models and fields

def update_database_schema():
    app = create_app(Config)
    
    with app.app_context():
        # Get the database path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            print(f"Database file not found at {db_path}")
            return
        
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists and add profile_image and bio columns if needed
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'profile_image' not in columns:
            print("Adding profile_image column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN profile_image VARCHAR(255)")
        
        if 'bio' not in columns:
            print("Adding bio column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")
        
        # Create review_images table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='review_images'")
        if not cursor.fetchone():
            print("Creating review_images table...")
            cursor.execute("""
            CREATE TABLE review_images (
                id INTEGER PRIMARY KEY,
                review_id INTEGER NOT NULL,
                image_url VARCHAR(255) NOT NULL,
                caption VARCHAR(255),
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (review_id) REFERENCES reviews (id)
            )
            """)
        
        # Create menu_item_review_images table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='menu_item_review_images'")
        if not cursor.fetchone():
            print("Creating menu_item_review_images table...")
            cursor.execute("""
            CREATE TABLE menu_item_review_images (
                id INTEGER PRIMARY KEY,
                menu_item_review_id INTEGER NOT NULL,
                image_url VARCHAR(255) NOT NULL,
                caption VARCHAR(255),
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (menu_item_review_id) REFERENCES menu_item_reviews (id)
            )
            """)
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        # Create all tables that don't exist yet
        db.create_all()
        
        print("Database schema updated successfully!")

if __name__ == "__main__":
    update_database_schema()
