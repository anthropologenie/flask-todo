"""Setup script to create test database with sample data"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app, db, Todo

def setup_test_database():
    """Create database and populate with test data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Clear existing data
        Todo.query.delete()
        
        # Add sample todos
        sample_todos = [
            Todo(title='Welcome to the application', complete=False),
            Todo(title='Good Morning, have a nice day', complete=False),
        ]
        
        for todo in sample_todos:
            db.session.add(todo)
        
        db.session.commit()
        
        print(f"✅ Test database setup complete!")
        print(f"   Created {Todo.query.count()} todos")
        
        # Verify
        all_todos = Todo.query.all()
        for todo in all_todos:
            print(f"   - {todo.id}: {todo.title} (complete={todo.complete})")

if __name__ == '__main__':
    setup_test_database()