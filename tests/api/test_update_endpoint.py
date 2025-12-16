"""
Test GET /update/<id> endpoint - Toggle todo complete status

Tests:
- Toggle incomplete to complete
- Toggle complete to incomplete
- Invalid IDs
- Database verification
"""
import pytest
from app import Todo


class TestUpdateEndpoint:
    """Test suite for GET /update/<id> endpoint"""
    
    def test_update_toggles_incomplete_to_complete(self, api_client, todo_factory, app):
        """Test toggling incomplete todo to complete"""
        # Create incomplete todo
        todo = todo_factory('Test toggle to complete', complete=False)
        todo_id = todo.id
        
        # Toggle via API
        response = api_client.get(f'/update/{todo_id}')
        
        assert response.status_code == 302
        assert response.location == '/'
        
        # Verify in database
        with app.app_context():
            updated_todo = Todo.query.get(todo_id)
            assert updated_todo.complete is True
        
        print(f"\n✅ Todo {todo_id} toggled: False → True")
    
    def test_update_toggles_complete_to_incomplete(self, api_client, todo_factory, app):
        """Test toggling complete todo back to incomplete"""
        # Create complete todo
        todo = todo_factory('Test toggle to incomplete', complete=True)
        todo_id = todo.id
        
        # Toggle via API
        response = api_client.get(f'/update/{todo_id}')
        
        assert response.status_code == 302
        
        # Verify in database
        with app.app_context():
            updated_todo = Todo.query.get(todo_id)
            assert updated_todo.complete is False
        
        print(f"\n✅ Todo {todo_id} toggled: True → False")
    
    def test_update_multiple_toggles(self, api_client, todo_factory, app):
        """Test toggling same todo multiple times"""
        todo = todo_factory('Multi-toggle test', complete=False)
        todo_id = todo.id
        
        # Toggle 4 times
        for i in range(4):
            response = api_client.get(f'/update/{todo_id}')
            assert response.status_code == 302
        
        # After 4 toggles, should be back to False
        with app.app_context():
            final_todo = Todo.query.get(todo_id)
            assert final_todo.complete is False
        
        print(f"\n✅ Todo {todo_id} toggled 4 times: back to original state")
    
    def test_update_does_not_modify_title(self, api_client, todo_factory, app):
        """Test that update only changes complete status, not title"""
        original_title = 'Original title should not change'
        todo = todo_factory(original_title, complete=False)
        todo_id = todo.id
        
        # Toggle
        api_client.get(f'/update/{todo_id}')
        
        # Verify title unchanged
        with app.app_context():
            updated_todo = Todo.query.get(todo_id)
            assert updated_todo.title == original_title
            assert updated_todo.complete is True
        
        print(f"\n✅ Todo {todo_id} title unchanged after update")
    
    def test_update_redirects_to_home(self, api_client, todo_factory):
        """Test that update redirects to homepage"""
        todo = todo_factory('Test redirect', complete=False)
        
        response = api_client.get(f'/update/{todo.id}', follow_redirects=False)
        
        assert response.status_code == 302
        assert response.location == '/'
        
        print(f"\n✅ Update redirects to homepage")


class TestUpdateEndpointEdgeCases:
    """Test edge cases for update endpoint"""
    
    def test_update_nonexistent_id(self, api_client, empty_database):
        """Test updating todo with ID that doesn't exist - BUG: App crashes"""
        nonexistent_id = 99999
    
        # BUG: App crashes instead of handling gracefully
        with pytest.raises(Exception):
            response = api_client.get(f'/update/{nonexistent_id}')
    
        print(f"\n⚠️  DOCUMENTED BUG: Update crashes on non-existent ID {nonexistent_id}")
        print("   Expected: 404 Not Found")  
        print("   Actual: AttributeError crash")
    
    def test_update_with_invalid_id_type(self, api_client, empty_database):
        """Test update with non-integer ID"""
        invalid_ids = ['abc', '1.5', 'null', '-1']
        
        for invalid_id in invalid_ids:
            response = api_client.get(f'/update/{invalid_id}')
            
            # Flask routing should handle this
            print(f"\n📝 Invalid ID '{invalid_id}': status {response.status_code}")
    
    def test_update_does_not_affect_other_todos(self, api_client, sample_todos, app):
        """Test that updating one todo doesn't affect others"""
        # Get states before update
        with app.app_context():
            original_states = {t.id: t.complete for t in Todo.query.all()}
        
        # Update first todo
        first_id = list(original_states.keys())[0]
        api_client.get(f'/update/{first_id}')
        
        # Verify only first todo changed
        with app.app_context():
            for todo in Todo.query.all():
                if todo.id == first_id:
                    assert todo.complete != original_states[todo.id]
                else:
                    assert todo.complete == original_states[todo.id]
        
        print(f"\n✅ Updating todo {first_id} didn't affect other todos")


class TestUpdateEndpointWithPandas:
    """Test update endpoint with pandas validation"""
    
    def test_update_verify_with_dataframe(self, api_client, todo_factory, app, actual_db_path):
        """Test update and verify using pandas DataFrame"""
        from tests.utils.df_helpers import load_todos_as_dataframe
        
        # Create todo
        todo = todo_factory('Pandas update test', complete=False)
        todo_id = todo.id
        
        # Update via API
        api_client.get(f'/update/{todo_id}')
        
        # Verify with pandas
        df = load_todos_as_dataframe(actual_db_path)
        updated_row = df[df['id'] == todo_id]
        
        assert len(updated_row) == 1
        assert updated_row['complete'].iloc[0] == 1  # SQLite stores True as 1
        
        print(f"\n✅ Pandas verification: Todo {todo_id} complete=1")
        print(updated_row.to_string(index=False))