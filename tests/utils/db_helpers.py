"""Database helper functions for tests"""
import sqlite3
from pathlib import Path

def get_db_connection(db_path):
    """
    Create a database connection
    
    Args:
        db_path: Path to SQLite database file
    
    Returns:
        sqlite3.Connection object
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def get_all_todos(db_path):
    """
    Fetch all todos from database
    
    Args:
        db_path: Path to SQLite database
    
    Returns:
        List of Row objects
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todo ORDER BY id")
    todos = cursor.fetchall()
    conn.close()
    return todos


def get_todo_by_id(db_path, todo_id):
    """
    Fetch specific todo by ID
    
    Args:
        db_path: Path to SQLite database
        todo_id: ID of todo to fetch
    
    Returns:
        Row object or None
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todo WHERE id = ?", (todo_id,))
    todo = cursor.fetchone()
    conn.close()
    return todo


def count_todos(db_path):
    """
    Count total todos in database
    
    Args:
        db_path: Path to SQLite database
    
    Returns:
        Integer count
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM todo")
    count = cursor.fetchone()['count']
    conn.close()
    return count


def get_schema(db_path):
    """
    Get table schema definition
    
    Args:
        db_path: Path to SQLite database
    
    Returns:
        String containing CREATE TABLE statement
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='todo'")
    schema = cursor.fetchone()
    conn.close()
    return schema['sql'] if schema else None


def insert_todo_directly(db_path, title, complete=0):
    """
    Insert todo directly via SQL (bypass Flask for testing)
    
    Args:
        db_path: Path to SQLite database
        title: Todo title
        complete: Complete status (0 or 1)
    
    Returns:
        ID of inserted todo
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO todo (title, complete) VALUES (?, ?)", (title, complete))
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()
    return todo_id


def delete_todo_directly(db_path, todo_id):
    """
    Delete todo directly via SQL
    
    Args:
        db_path: Path to SQLite database
        todo_id: ID of todo to delete
    
    Returns:
        Number of rows deleted
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todo WHERE id = ?", (todo_id,))
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    return rows_deleted


def update_todo_directly(db_path, todo_id, complete):
    """
    Update todo complete status directly via SQL
    
    Args:
        db_path: Path to SQLite database
        todo_id: ID of todo to update
        complete: New complete status (0 or 1)
    
    Returns:
        Number of rows updated
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE todo SET complete = ? WHERE id = ?", (complete, todo_id))
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()
    return rows_updated


def clear_all_todos(db_path):
    """
    Delete all todos from database (for test cleanup)
    
    Args:
        db_path: Path to SQLite database
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todo")
    conn.commit()
    conn.close()