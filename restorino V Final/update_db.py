from app import create_app
from models import db, Restaurant, MenuItem, MenuItemReview, ChallengePost, ChallengeComment, Tourist, ChallengeParticipant, Category
from config import Config
import sqlite3
import os
import shutil

# This script will update the database schema to include the new models and fields
# Run this script after updating the models.py file

def add_column_if_not_exists(conn, table_name, column_name, column_type):
    """Add a column to a table if it doesn't already exist"""
    cursor = conn.cursor()
    # Check if the column exists
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    
    if column_name not in columns:
        print(f"Adding column {column_name} to {table_name}")
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        conn.commit()
        return True
    return False

# Get the database path from the config
app = create_app(Config)
db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

# Create a backup of the database
if os.path.exists(db_path):
    backup_path = db_path + '.backup'
    print(f"Creating backup of database at {backup_path}")
    shutil.copy2(db_path, backup_path)

# Option 1: Recreate the database from scratch (this will lose all data)
recreate_db = False
if recreate_db and os.path.exists(db_path):
    print("Recreating database from scratch...")
    os.remove(db_path)

with app.app_context():
    # Create all tables (this will create any missing tables)
    db.create_all()
    
    # Connect to the SQLite database directly to add columns if needed
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        
        # Add missing columns to the restaurants table
        add_column_if_not_exists(conn, 'restaurants', 'address', 'TEXT')
        add_column_if_not_exists(conn, 'restaurants', 'latitude', 'FLOAT')
        add_column_if_not_exists(conn, 'restaurants', 'longitude', 'FLOAT')
        add_column_if_not_exists(conn, 'restaurants', 'whatsapp_number', 'TEXT')
        add_column_if_not_exists(conn, 'restaurants', 'website', 'TEXT')
        add_column_if_not_exists(conn, 'restaurants', 'instagram', 'TEXT')
        add_column_if_not_exists(conn, 'restaurants', 'facebook', 'TEXT')
        add_column_if_not_exists(conn, 'restaurants', 'vibe_inside', 'TEXT')
        add_column_if_not_exists(conn, 'restaurants', 'vibe_outside', 'TEXT')
        add_column_if_not_exists(conn, 'restaurants', 'is_claimed', 'BOOLEAN')
        add_column_if_not_exists(conn, 'restaurants', 'features', 'TEXT')
        add_column_if_not_exists(conn, 'restaurants', 'category_id', 'INTEGER')
        add_column_if_not_exists(conn, 'restaurants', 'price_range', 'TEXT')
        
        # Add missing columns to the tourists table
        add_column_if_not_exists(conn, 'tourists', 'instagram', 'TEXT')
        add_column_if_not_exists(conn, 'tourists', 'twitter', 'TEXT')
        add_column_if_not_exists(conn, 'tourists', 'facebook', 'TEXT')
        add_column_if_not_exists(conn, 'tourists', 'tiktok', 'TEXT')
        
        # Add missing columns to the challenge_participants table
        add_column_if_not_exists(conn, 'challenge_participants', 'created_at', 'TIMESTAMP')
        add_column_if_not_exists(conn, 'challenge_participants', 'comment', 'TEXT')
        add_column_if_not_exists(conn, 'challenge_participants', 'social_post_url', 'TEXT')
        
        conn.close()
    
    # Refresh SQLAlchemy's view of the database schema
    print("Refreshing SQLAlchemy metadata...")
    db.metadata.clear()
    db.reflect()
    db.session.commit()
    
    print("Database updated successfully!")
