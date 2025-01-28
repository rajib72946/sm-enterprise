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
        # Create settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create pages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS page (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                content TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add default contact settings
        cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', 
                      ('contact_phone', '+919876543210'))
        cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', 
                      ('contact_whatsapp', '919876543210'))
        cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', 
                      ('shop_name', 'S.M. Enterprise'))
        
        # Add default pages
        cursor.execute('INSERT OR IGNORE INTO page (title, slug, content) VALUES (?, ?, ?)',
                      ('About Us', 'about', '<h2>Welcome to Our Mobile Shop</h2><p>We are dedicated to providing the best quality used and new mobile phones at competitive prices.</p>'))
        cursor.execute('INSERT OR IGNORE INTO page (title, slug, content) VALUES (?, ?, ?)',
                      ('Contact Us', 'contact', '<h2>Get in Touch</h2><p>We are here to help! Contact us through the following methods:</p>'))
        
        # Commit the changes
        conn.commit()
        print("Migration successful: Added settings and pages tables with default data")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    run_migration()
