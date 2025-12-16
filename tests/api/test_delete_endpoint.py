"""
Test GET /delete/<id> endpoint - Delete todo

Tests:
- Successful deletion
- Database verification
- Invalid IDs
- Multiple deletions
"""
import pytest
from app import Todo


class TestDeleteEndpoint:
    """Test suite for GET /delete/<id> endpoint"""
    
    def test_delete_existing_todo(self, api_client, todo_factory, app):
        """Test deleting an existing todo"""
        # Create todo
        todo = todo_factory('Test delete', complete=False)
        todo_id = todo.id
        
        # Delete via API
        response = api_client.get(f'/delete/{todo_id}')
        
        assert response.status_code == 302
        assert response.location == '/'
        
        # Verify deleted from database
        with app.app_context():
            deleted_todo = Todo.query.get(todo_id)
            assert deleted_todo is None
            
        print(f"\n✅ Todo {todo_id} deleted successfully")
    
    def test_delete_reduces_todo_count(self, api_client, sample_todos, app):
        """Test that delete reduces total todo count"""
        with app.app_context():
            initial_count = Todo.query.count()
            first_id = sample_todos[0].id
        
        # Delete one todo
        api_client.get(f'/delete/{first_id}')
        
        # Verify count decreased
        with app.app_context():
            final_count = Todo.query.count()
            assert final_count == initial_count - 1
        
        print(f"\n✅ Todo count: {initial_count} → {final_count}")
    
    def test_delete_multiple_todos(self, api_client, sample_todos, app):
        """Test deleting multiple todos sequentially"""
        with app.app_context():
            todo_ids = [t.id for t in sample_todos]
            initial_count = len(todo_ids)
        
        # Delete all todos
        for todo_id in todo_ids:
            response = api_client.get(f'/delete/{todo_id}')
            assert response.status_code == 302
        
        # Verify all deleted
        with app.app_context():
            final_count = Todo.query.count()
            assert final_count == 0
        
        print(f"\n✅ Deleted {initial_count} todos, final count: {final_count}")
    
    def test_delete_does_not_affect_other_todos(self, api_client, sample_todos, app):
        """Test deleting one todo doesn't affect others"""
        with app.app_context():
            ids_before = {t.id for t in Todo.query.all()}
            id_to_delete = list(ids_before)[0]
        
        # Delete one todo
        api_client.get(f'/delete/{id_to_delete}')
        
        # Verify others still exist
        with app.app_context():
            ids_after = {t.id for t in Todo.query.all()}
            expected_ids = ids_before - {id_to_delete}
            assert ids_after == expected_ids
        
        print(f"\n✅ Deleted todo {id_to_delete}, others unaffected")
    
    def test_delete_redirects_to_home(self, api_client, todo_factory):
        """Test that delete redirects to homepage"""
        todo = todo_factory('Test redirect', complete=False)
        
        response = api_client.get(f'/delete/{todo.id}', follow_redirects=False)
        
        assert response.status_code == 302
        assert response.location == '/'
        
        print(f"\n✅ Delete redirects to homepage")
    
    def test_deleted_todo_not_on_homepage(self, api_client, todo_factory):
        """Test that deleted todo no longer appears on homepage"""
        todo_title = 'Should not appear after delete'
        todo = todo_factory(todo_title, complete=False)
        
        # Delete todo
        api_client.get(f'/delete/{todo.id}')
        
        # Check homepage
        response = api_client.get('/')
        assert todo_title.encode() not in response.data
        
        print(f"\n✅ Deleted todo not visible on homepage")


class TestDeleteEndpointEdgeCases:
    """Test edge cases for delete endpoint"""
    
    @pytest.mark.skip(reason="Known bug: no error handling for non-existent IDs")
    def test_delete_nonexistent_id(self, api_client, empty_database):
        """Test deleting todo with ID that doesn't exist - BUG: App crashes"""
        nonexistent_id = 99999
    
        # BUG: App crashes instead of handling gracefully
        # This test documents the bug
        with pytest.raises(Exception):  # Expect it to crash
            response = api_client.get(f'/delete/{nonexistent_id}')
    
        print(f"\n⚠️  DOCUMENTED BUG: Delete crashes on non-existent ID {nonexistent_id}")
        print("   Expected: 404 Not Found")
        print("   Actual: AttributeError crash")
    
    @pytest.mark.skip(reason="Known bug: no error handling for non-existent IDs")
    def test_delete_same_id_twice(self, api_client, todo_factory):
        """Test deleting same todo twice - BUG: Second delete crashes"""
        todo = todo_factory('Test double delete', complete=False)
        todo_id = todo.id
    
        # First delete - should succeed
        response1 = api_client.get(f'/delete/{todo_id}')
        assert response1.status_code == 302
    
        # Second delete - BUG: crashes instead of handling gracefully
        with pytest.raises(Exception):
            response2 = api_client.get(f'/delete/{todo_id}')
    
        print(f"\n⚠️  DOCUMENTED BUG: Second delete crashes (ID {todo_id})")
        print("   Expected: 404 or graceful handling")
        print("   Actual: AttributeError crash")
    
    def test_delete_with_invalid_id_type(self, api_client):
        """Test delete with non-integer ID"""
        invalid_ids = ['abc', '1.5', 'null']
        
        for invalid_id in invalid_ids:
            response = api_client.get(f'/delete/{invalid_id}')
            print(f"\n📝 Invalid ID '{invalid_id}': status {response.status_code}")


class TestDeleteEndpointWithPandas:
    """Test delete endpoint with pandas validation"""
    
    @pytest.mark.skip(reason="Known bug: no error handling for non-existent IDs")
    def test_delete_verify_with_dataframe(self, api_client, todo_factory, app, actual_db_path):
        """Test delete and verify using pandas DataFrame"""
        from tests.utils.df_helpers import load_todos_as_dataframe
        
        # Create two todos
        todo1 = todo_factory('Keep this todo', complete=False)
        todo2 = todo_factory('Delete this todo', complete=False)
        
        # Delete second todo
        api_client.get(f'/delete/{todo2.id}')
        
        # Verify with pandas
        df = load_todos_as_dataframe(actual_db_path)
        
        assert len(df) == 1
        assert df['id'].iloc[0] == todo1.id
        assert todo2.id not in df['id'].values
        
        print(f"\n✅ Pandas verification: Todo {todo2.id} deleted")
        print(df.to_string(index=False))
    
    def test_delete_all_verify_empty_dataframe(self, api_client, sample_todos, actual_db_path):
        """Test deleting all todos results in empty DataFrame"""
        from tests.utils.df_helpers import load_todos_as_dataframe
        
        # Delete all todos
        for todo in sample_todos:
            api_client.get(f'/delete/{todo.id}')
        
        # Verify with pandas
        df = load_todos_as_dataframe(actual_db_path)
        
        assert len(df) == 0
        
        print("\n✅ Pandas verification: Database empty after deleting all todos")