from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os

def run_migration():
    # Connect to the database
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'shop.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Add original_price column
        cursor.execute('ALTER TABLE mobile ADD COLUMN original_price FLOAT')
        
        # Update existing records to have the same price as original_price
        cursor.execute('UPDATE mobile SET original_price = price')
        
        # Commit the changes
        conn.commit()
        print("Migration successful: Added original_price column")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column original_price already exists")
        else:
            raise e
    finally:
        conn.close()

if __name__ == '__main__':
    run_migration()
