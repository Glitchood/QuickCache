import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect("quickcache.db")
cursor = conn.cursor()

# Create tables
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER,
    server_id INTEGER,
    PRIMARY KEY (user_id, server_id)
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS caches (
    cache_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    server_id INTEGER,
    FOREIGN KEY (user_id, server_id) REFERENCES users(user_id, server_id)
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_id INTEGER,
    tag TEXT,
    FOREIGN KEY (cache_id) REFERENCES caches(cache_id)
)
"""
)

conn.commit()
