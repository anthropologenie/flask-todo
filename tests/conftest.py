"""Pytest configuration and fixtures"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app as flask_app, db
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