"""
This is an example of a secure database connection in Python.
It demonstrates using a context manager (`with`) for the connection
and cursor, which ensures resources are automatically cleaned up.
It also shows how to use parameterized queries to prevent SQL injection.
"""
import sqlite3

def get_user_by_id(db_path, user_id):
    """
    Fetches a user from the database securely.

    Args:
        db_path (str): The path to the SQLite database.
        user_id (int): The ID of the user to fetch.

    Returns:
        tuple: The user record, or None if not found or an error occurs.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            with conn.cursor() as cursor:
                # Use a parameterized query to prevent SQL injection.
                # The '?' is a placeholder for the user_id.
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                user_record = cursor.fetchone()
                return user_record
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
