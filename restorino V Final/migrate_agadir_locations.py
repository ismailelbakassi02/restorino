"""
Migration script to add the AgadirLocation table and update the Restaurant table
with a foreign key reference to AgadirLocation.
"""
from models import db, AgadirLocation, Restaurant
from config import Config

# Create a minimal app for the migration
from flask import Flask

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    return app

def migrate():
    """Run the migration to add AgadirLocation table and update Restaurant table"""
    print("Starting migration...")
    
    # Create the application context
    app = create_app(Config)
    with app.app_context():
        # Step 1: Create the AgadirLocation table if it doesn't exist
        print("Creating AgadirLocation table...")
        
        # Check if the table exists first
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'agadir_locations' not in tables:
            # Create only the AgadirLocation table
            AgadirLocation.__table__.create(db.engine, checkfirst=True)
            print("Created AgadirLocation table")
        else:
            print("AgadirLocation table already exists")
        
        # Step 2: Check if we need to add the location_id column to the Restaurant table
        restaurant_columns = [column['name'] for column in inspector.get_columns('restaurants')]
        if 'location_id' not in restaurant_columns and 'restaurants' in tables:
            print("Adding location_id column to Restaurant table...")
            # Use raw SQL to add the column since SQLAlchemy doesn't support schema modifications
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE restaurants ADD COLUMN location_id INTEGER REFERENCES agadir_locations(id)'))
                conn.commit()
            print("Added location_id column to Restaurant table")
        
        # Step 3: Populate the AgadirLocation table with initial data if empty
        if AgadirLocation.query.count() == 0:
            print("Populating AgadirLocation table with initial data...")
            # Add default Agadir locations
            default_locations = [
                {"name": "Talborjt", "description": "Historic district in the heart of Agadir"},
                {"name": "Marina", "description": "Modern marina area with shops and restaurants"},
                {"name": "Founty", "description": "Upscale area with luxury hotels and restaurants"},
                {"name": "Sonaba", "description": "Beach area with many tourist attractions"},
                {"name": "Dakhla", "description": "Residential area with local restaurants"},
                {"name": "Charaf", "description": "Commercial district with various businesses"},
                {"name": "Tikiouine", "description": "Industrial area on the outskirts of Agadir"},
                {"name": "Cite Suisse", "description": "Residential neighborhood with local cuisine"},
                {"name": "Hay Mohammadi", "description": "Vibrant area with authentic local food"}
            ]
            
            for location_data in default_locations:
                location = AgadirLocation(
                    name=location_data["name"],
                    description=location_data["description"]
                )
                db.session.add(location)
            
            db.session.commit()
            print(f"Added {len(default_locations)} default locations to the database")
        
        # Step 4: Only try to update restaurants if the location_id column exists
        if 'location_id' in restaurant_columns or ('restaurants' in tables and 'location_id' not in restaurant_columns):
            try:
                print("Updating existing restaurants with location references...")
                # Use raw SQL to avoid ORM issues with the new column
                with db.engine.connect() as conn:
                    result = conn.execute(db.text('SELECT id, location FROM restaurants'))
                    restaurants = result.fetchall()
                    
                    locations = {location.name.lower(): location for location in AgadirLocation.query.all()}
                    
                    updated_count = 0
                    for row in restaurants:
                        restaurant_id = row[0]
                        restaurant_location = row[1]
                        if restaurant_location:
                            restaurant_location = restaurant_location.lower()
                            for location_name, location in locations.items():
                                if location_name in restaurant_location or restaurant_location in location_name:
                                    conn.execute(db.text(f"UPDATE restaurants SET location_id = {location.id} WHERE id = {restaurant_id}"))
                                    updated_count += 1
                                    break
                    
                    conn.commit()
                
                print(f"Updated {updated_count} restaurants with location references")
            except Exception as e:
                print(f"Error updating restaurants: {e}")
        
        print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
