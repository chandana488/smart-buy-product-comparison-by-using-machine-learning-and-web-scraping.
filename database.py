import sqlite3
import os

DB_NAME = 'dealtracker.db'

def get_db_connection():
    """Establish and return a database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            website TEXT NOT NULL,
            price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_product(product_name, website, price):
    """Save a scraped product into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO products (product_name, website, price)
        VALUES (?, ?, ?)
    ''', (product_name, website, price))
    
    conn.commit()
    conn.close()

def get_product_history(product_name):
    """Fetch the price history for a given product name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Use LIKE for loose matching
    cursor.execute('''
        SELECT product_name, website, price, timestamp
        FROM products
        WHERE product_name LIKE ?
        ORDER BY timestamp ASC
    ''', (f"%{product_name}%",))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
