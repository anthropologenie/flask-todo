"""Test configuration settings"""
import os
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

class TestConfig:
    """Configuration for unit tests with in-memory database"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

class IntegrationTestConfig:
    """Configuration for integration tests using actual database"""
    TESTING = True
    # Use a copy of the real database for integration tests
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{PROJECT_ROOT}/instance/db.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Path to actual database for pandas validation tests
ACTUAL_DB_PATH = PROJECT_ROOT / 'instance' / 'db.sqlite'
TEST_DB_PATH = PROJECT_ROOT / 'tests' / 'test_db.sqlite'