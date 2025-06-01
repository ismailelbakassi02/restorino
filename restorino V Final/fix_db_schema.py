from app import create_app
from models import db
from config import Config
import sqlite3
import os

# This script will fix the database schema issues with the menu_items table

def fix_menu_items_table():
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
        
        # Check if menu_items table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='menu_items'")
        if not cursor.fetchone():
            print("menu_items table doesn't exist. Creating tables from scratch.")
            db.create_all()
            conn.close()
            return
        
        # Get current column information
        cursor.execute("PRAGMA table_info(menu_items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Create a new table with the correct schema
        print("Creating temporary table with correct schema...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items_new (
            id INTEGER PRIMARY KEY,
            restaurant_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            price FLOAT NOT NULL,
            image_url VARCHAR(255),
            ingredients TEXT,
            preparation_time VARCHAR(20),
            is_vegetarian BOOLEAN DEFAULT 0,
            is_vegan BOOLEAN DEFAULT 0,
            is_gluten_free BOOLEAN DEFAULT 0,
            spice_level INTEGER DEFAULT 0,
            average_rating FLOAT DEFAULT 0.0,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
        )
        """)
        
        # Copy existing data
        if 'image_url' in columns:
            # If image_url exists, copy all data
            print("Copying existing data with image_url...")
            cursor.execute("""
            INSERT INTO menu_items_new (id, restaurant_id, name, description, price, 
                                       image_url, ingredients, preparation_time, 
                                       is_vegetarian, is_vegan, is_gluten_free, 
                                       spice_level, average_rating)
            SELECT id, restaurant_id, name, description, price, 
                   image_url, ingredients, preparation_time, 
                   is_vegetarian, is_vegan, is_gluten_free, 
                   spice_level, average_rating
            FROM menu_items
            """)
        else:
            # If image_url doesn't exist, copy data without it
            print("Copying existing data without image_url...")
            cursor.execute("""
            INSERT INTO menu_items_new (id, restaurant_id, name, description, price)
            SELECT id, restaurant_id, name, description, price
            FROM menu_items
            """)
        
        # Replace the old table with the new one
        print("Replacing old table with new table...")
        cursor.execute("DROP TABLE menu_items")
        cursor.execute("ALTER TABLE menu_items_new RENAME TO menu_items")
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        print("Database schema fixed successfully!")

if __name__ == "__main__":
    fix_menu_items_table()
