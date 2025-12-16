"""Pytest configuration and fixtures"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app as flask_app, db, Todo
from tests.config.test_config import ACTUAL_DB_PATH


@pytest.fixture(scope='session')
def app():
    """
    Create Flask application for testing (session-scoped)
    Uses in-memory database for unit tests
    """
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for making HTTP requests"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner for testing Flask commands"""
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """Database session for tests (function-scoped, rolls back after each test)"""
    with app.app_context():
        # Start a transaction
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Bind session to this transaction
        session = db.session
        
        yield session
        
        # Rollback transaction after test
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope='module')
def actual_db_path():
    """
    Path to actual database for integration/pandas tests
    This points to the real instance/db.sqlite file
    """
    return ACTUAL_DB_PATH


@pytest.fixture
def sample_todo_data():
    """Sample todo data for testing"""
    return [
        {'title': 'Test task 1', 'complete': False},
        {'title': 'Test task 2', 'complete': True},
        {'title': 'Test task 3', 'complete': False},
    ]


# ============================================
# API Testing Fixtures
# ============================================

@pytest.fixture
def api_client(app):
    """Flask test client for API testing"""
    return app.test_client()


@pytest.fixture
def sample_todos(app, db_session):
    """Create sample todos in database for testing"""
    with app.app_context():
        # Clear existing data
        Todo.query.delete()
        
        # Add sample todos
        todos = [
            Todo(title='Sample task 1', complete=False),
            Todo(title='Sample task 2', complete=True),
            Todo(title='Sample task 3', complete=False),
        ]
        
        for todo in todos:
            db_session.add(todo)
        
        db_session.commit()
        
        # Return list of created todos
        return Todo.query.all()


@pytest.fixture
def empty_database(app, db_session):
    """Ensure database is empty before test"""
    with app.app_context():
        Todo.query.delete()
        db_session.commit()


@pytest.fixture
def todo_factory(app, db_session):
    """Factory fixture to create todos on demand"""
    def _create_todo(title, complete=False):
        with app.app_context():
            todo = Todo(title=title, complete=complete)
            db_session.add(todo)
            db_session.commit()
            db_session.refresh(todo)  # Get the ID
            return todo
    
    return _create_todo