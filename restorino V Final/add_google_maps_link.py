"""
Migration script to add the google_maps_link column to the Restaurant table.
"""
from models import db
from config import Config

# Create a minimal app for the migration
from flask import Flask

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    return app

def migrate():
    """Run the migration to add the google_maps_link column to the Restaurant table"""
    print("Starting migration...")
    
    # Create the application context
    app = create_app(Config)
    with app.app_context():
        # Check if the column exists first
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'restaurants' in tables:
            restaurant_columns = [column['name'] for column in inspector.get_columns('restaurants')]
            if 'google_maps_link' not in restaurant_columns:
                print("Adding google_maps_link column to Restaurant table...")
                # Use raw SQL to add the column since SQLAlchemy doesn't support schema modifications
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE restaurants ADD COLUMN google_maps_link VARCHAR(500)'))
                    conn.commit()
                print("Added google_maps_link column to Restaurant table")
            else:
                print("google_maps_link column already exists in Restaurant table")
        else:
            print("restaurants table doesn't exist yet, no migration needed")
        
        print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
