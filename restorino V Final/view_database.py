import sqlite3
import os

def view_database():
    """View the contents of the SQLite database"""
    # Connect to the database
    db_path = os.path.join('instance', 'database.db')
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("\n=== DATABASE TABLES ===")
    for table in tables:
        table_name = table[0]
        print(f"\n--- TABLE: {table_name} ---")
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print("Columns:", ", ".join(column_names))
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        print(f"Row count: {row_count}")
        
        # Show sample data (up to 5 rows)
        if row_count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            
            print("\nSample data:")
            for row in rows:
                formatted_row = [str(item) if item is not None else "NULL" for item in row]
                print(" | ".join(formatted_row))
    
    # Close connection
    conn.close()

if __name__ == "__main__":
    view_database()
