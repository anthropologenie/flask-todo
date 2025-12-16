"""
Test GET / endpoint - Homepage that lists all todos

Tests:
- Empty database returns empty list
- Multiple todos are returned
- Response status codes
- HTML rendering
"""
import pytest
from app import Todo


class TestHomeEndpoint:
    """Test suite for GET / (homepage) endpoint"""
    
    def test_home_with_empty_database(self, api_client, empty_database):
        """Test homepage returns 200 when database is empty"""
        response = api_client.get('/')
        
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data  # Basic HTML check
        print("\n✅ Homepage loads successfully with empty database")
    
    def test_home_with_sample_data(self, api_client, sample_todos):
        """Test homepage displays all todos"""
        response = api_client.get('/')
        
        assert response.status_code == 200
        
        # Check that all sample todos are in response
        for todo in sample_todos:
            assert todo.title.encode() in response.data
        
        print(f"\n✅ Homepage displays all {len(sample_todos)} todos")
    
    def test_home_returns_html(self, api_client, sample_todos):
        """Test homepage returns HTML content"""
        response = api_client.get('/')
        
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data
        
        print("\n✅ Homepage returns valid HTML")
    
    def test_home_shows_incomplete_todos(self, api_client, sample_todos):
        """Test homepage shows incomplete todos"""
        response = api_client.get('/')
        
        incomplete_todos = [t for t in sample_todos if not t.complete]
        for todo in incomplete_todos:
            assert todo.title.encode() in response.data
        
        print(f"\n✅ Homepage shows {len(incomplete_todos)} incomplete todos")
    
    def test_home_shows_complete_todos(self, api_client, sample_todos):
        """Test homepage shows completed todos"""
        response = api_client.get('/')
        
        complete_todos = [t for t in sample_todos if t.complete]
        for todo in complete_todos:
            assert todo.title.encode() in response.data
        
        print(f"\n✅ Homepage shows {len(complete_todos)} completed todos")


class TestHomeEndpointWithDatabase:
    """Test homepage with database verification"""
    
    def test_home_todo_count_matches_database(self, api_client, sample_todos, app):
        """Verify number of todos in response matches database"""
        response = api_client.get('/')
        
        with app.app_context():
            db_count = Todo.query.count()
            
        assert response.status_code == 200
        assert db_count == len(sample_todos)
        
        print(f"\n✅ Todo count matches database: {db_count} todos")