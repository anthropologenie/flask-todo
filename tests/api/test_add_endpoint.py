"""
Test POST /add endpoint - Create new todo

Tests:
- Valid todo creation
- Empty title handling
- Special characters
- Database verification
- Redirects
"""
import pytest
from app import Todo
from tests.utils.db_helpers import count_todos


class TestAddEndpoint:
    """Test suite for POST /add endpoint"""
    
    def test_add_todo_with_valid_data(self, api_client, empty_database, app, actual_db_path):
        """Test adding a valid todo"""
        # Add todo via API
        response = api_client.post('/add', data={'title': 'New test task'}, follow_redirects=False)
        
        # Should redirect to home
        assert response.status_code == 302
        assert response.location == '/'
        
        # Verify in database
        with app.app_context():
            todos = Todo.query.all()
            assert len(todos) == 1
            assert todos[0].title == 'New test task'
            assert todos[0].complete is False
        
        print("\n✅ Todo added successfully with valid data")
    
    def test_add_todo_increments_id(self, api_client, empty_database, app):
        """Test that IDs auto-increment correctly"""
        # Add first todo
        api_client.post('/add', data={'title': 'First task'})
        
        with app.app_context():
            first_todo = Todo.query.first()
            first_id = first_todo.id
        
        # Add second todo
        api_client.post('/add', data={'title': 'Second task'})
        
        with app.app_context():
            second_todo = Todo.query.filter_by(title='Second task').first()
            second_id = second_todo.id
            
            assert second_id > first_id
            assert Todo.query.count() == 2
        
        print(f"\n✅ IDs auto-increment correctly: {first_id} → {second_id}")
    
    def test_add_todo_defaults_to_incomplete(self, api_client, empty_database, app):
        """Test that new todos default to complete=False"""
        api_client.post('/add', data={'title': 'Test default status'})
        
        with app.app_context():
            todo = Todo.query.first()
            assert todo.complete is False
        
        print("\n✅ New todos default to incomplete (complete=False)")
    
    def test_add_multiple_todos(self, api_client, empty_database, app):
        """Test adding multiple todos in sequence"""
        titles = ['Task 1', 'Task 2', 'Task 3', 'Task 4', 'Task 5']
        
        for title in titles:
            response = api_client.post('/add', data={'title': title})
            assert response.status_code == 302
        
        with app.app_context():
            todos = Todo.query.all()
            assert len(todos) == 5
            
            # Verify all titles exist
            todo_titles = [t.title for t in todos]
            for title in titles:
                assert title in todo_titles
        
        print(f"\n✅ Added {len(titles)} todos successfully")
    
    def test_add_redirects_to_home(self, api_client, empty_database):
        """Test that POST /add redirects to homepage"""
        response = api_client.post('/add', data={'title': 'Test redirect'}, follow_redirects=False)
        
        assert response.status_code == 302
        assert response.location == '/'
        
        print("\n✅ POST /add redirects to homepage")
    
    def test_add_and_verify_on_homepage(self, api_client, empty_database):
        """Test that added todo appears on homepage"""
        task_title = 'Verify on homepage'
        
        # Add todo
        api_client.post('/add', data={'title': task_title})
        
        # Get homepage
        response = api_client.get('/')
        
        assert task_title.encode() in response.data
        
        print("\n✅ Added todo appears on homepage")


class TestAddEndpointEdgeCases:
    """Test edge cases for POST /add endpoint"""
    
    def test_add_empty_title(self, api_client, empty_database, app):
        """Test behavior when adding empty title"""
        response = api_client.post('/add', data={'title': ''})
        
        # App currently accepts empty titles (document this behavior)
        assert response.status_code == 302
        
        with app.app_context():
            todos = Todo.query.all()
            # Check if empty title was saved
            if len(todos) > 0:
                print("\n⚠️  App accepts empty titles (potential validation issue)")
            else:
                print("\n✅ App rejects empty titles")
    
    def test_add_whitespace_only_title(self, api_client, empty_database, app):
        """Test adding title with only whitespace"""
        response = api_client.post('/add', data={'title': '    '})
        
        assert response.status_code == 302
        
        with app.app_context():
            todos = Todo.query.all()
            if len(todos) > 0:
                todo = todos[0]
                print(f"\n⚠️  App accepts whitespace-only titles: '{todo.title}'")
    
    def test_add_long_title(self, api_client, empty_database, app):
        """Test adding title with 100+ characters"""
        long_title = 'A' * 150  # 150 characters
        
        response = api_client.post('/add', data={'title': long_title})
        assert response.status_code == 302
        
        with app.app_context():
            todo = Todo.query.first()
            if todo:
                actual_length = len(todo.title)
                print(f"\n📏 Title length: {actual_length} chars (input: 150 chars)")
                
                if actual_length == 150:
                    print("⚠️  No truncation - exceeds schema limit of 100")
                elif actual_length == 100:
                    print("✅ Title truncated to 100 chars")
    
    def test_add_special_characters(self, api_client, empty_database, app):
        """Test adding title with special characters"""
        special_titles = [
            "Task with <b>HTML</b> tags",
            "Task with 'quotes' and \"double quotes\"",
            "Task with émojis 🎉 ✅",
            "Task with symbols: @#$%^&*()",
        ]
        
        for title in special_titles:
            api_client.post('/add', data={'title': title})
        
        with app.app_context():
            todos = Todo.query.all()
            assert len(todos) == len(special_titles)
            
            print("\n✅ All special character titles saved:")
            for todo in todos:
                print(f"   - {todo.title}")
    
    def test_add_sql_injection_attempt(self, api_client, empty_database, app):
        """Test SQL injection protection"""
        sql_payload = "'; DROP TABLE todo; --"
        
        response = api_client.post('/add', data={'title': sql_payload})
        assert response.status_code == 302
        
        with app.app_context():
            # Table should still exist
            todos = Todo.query.all()
            assert len(todos) == 1
            
            # Payload should be stored as literal string
            assert todos[0].title == sql_payload
        
        print("\n✅ SQL injection blocked - payload stored as text")
    
    def test_add_without_title_parameter(self, api_client, empty_database, app):
        """Test POST /add without 'title' parameter"""
        response = api_client.post('/add', data={})
        
        # Should handle missing parameter
        assert response.status_code in [302, 400, 500]
        
        with app.app_context():
            todo_count = Todo.query.count()
            
        print(f"\n📝 Missing parameter handled (status: {response.status_code}, todos: {todo_count})")


class TestAddEndpointWithPandas:
    """Test POST /add with pandas DataFrame validation"""
    
    def test_add_and_verify_with_dataframe(self, api_client, empty_database, app, actual_db_path):
        """Test adding todo and verify using pandas"""
        from tests.utils.df_helpers import load_todos_as_dataframe
        
        # Add todo
        test_title = 'Pandas validation test'
        api_client.post('/add', data={'title': test_title})
        
        # Load database into DataFrame
        df = load_todos_as_dataframe(actual_db_path)
        
        # Verify with pandas
        assert len(df) == 1
        assert df['title'].iloc[0] == test_title
        assert df['complete'].iloc[0] == 0
        
        print(f"\n✅ Pandas verification successful:")
        print(df.to_string(index=False))