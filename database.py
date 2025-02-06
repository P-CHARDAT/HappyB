import psycopg2
import os

# Get the DATABASE_URL from environment variables (Railway)
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cursor = conn.cursor()

# Create table if it doesn’t exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS anniversaires (
    user_id BIGINT PRIMARY KEY,
    date TEXT NOT NULL
)
''')
conn.commit()

def add_birthday(user_id, date):
    """Add or update a user's birthday"""
    cursor.execute("INSERT INTO anniversaires (user_id, date) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET date = EXCLUDED.date", (user_id, date))
    conn.commit()

def get_all_birthdays():
    """Retrieve all birthdays"""
    cursor.execute("SELECT * FROM anniversaires")
    return cursor.fetchall()

def get_birthday(user_id):
    """Get a specific user's birthday"""
    cursor.execute("SELECT date FROM anniversaires WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def update_birthday(user_id, date):
    """Update a user's birthday"""
    cursor.execute("UPDATE anniversaires SET date = %s WHERE user_id = %s", (date, user_id))
    conn.commit()

def delete_birthday(user_id):
    """Delete a user's birthday"""
    cursor.execute("DELETE FROM anniversaires WHERE user_id = %s", (user_id,))
    conn.commit()
