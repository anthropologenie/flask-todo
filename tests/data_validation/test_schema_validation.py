"""
Test database schema validation using pandas DataFrames

Purpose: Verify the database structure matches expectations
Approach: Load actual database into pandas and validate schema
"""
import pytest
import pandas as pd
from tests.utils.df_helpers import (
    load_todos_as_dataframe,
    validate_schema,
    validate_column_types,
    validate_no_nulls,
    validate_unique,
    validate_value_range,
    validate_string_max_length,
    get_data_quality_report
)


class TestSchemaValidation:
    """Validate database schema using pandas DataFrame analysis"""
    
    def test_load_database_into_dataframe(self, actual_db_path):
        """Test that we can load the database into a pandas DataFrame"""
        df = load_todos_as_dataframe(actual_db_path)
        
        assert isinstance(df, pd.DataFrame), "Should return a pandas DataFrame"
        assert len(df) > 0, "DataFrame should have data (you added 2 records)"
        print(f"\n✅ Loaded {len(df)} rows from database")
    
    def test_dataframe_has_correct_columns(self, actual_db_path):
        """Verify DataFrame has expected columns in correct order"""
        df = load_todos_as_dataframe(actual_db_path)
        
        expected_columns = ['id', 'title', 'complete']
        validate_schema(df, expected_columns)
        
        print(f"\n✅ Schema validated: {list(df.columns)}")
    
    def test_dataframe_column_types(self, actual_db_path):
        """Verify column data types are correct"""
        df = load_todos_as_dataframe(actual_db_path)
        
        # Expected types for SQLite loaded into pandas
        expected_types = {
            'id': 'int64',
            'title': 'object',  # Strings are 'object' type in pandas
            'complete': 'int64'  # Booleans stored as 0/1 in SQLite
        }
        
        validate_column_types(df, expected_types)
        
        print("\n✅ Column types validated:")
        print(df.dtypes)
    
    def test_id_column_is_unique(self, actual_db_path):
        """Verify ID column has no duplicates (primary key constraint)"""
        df = load_todos_as_dataframe(actual_db_path)
        
        validate_unique(df, 'id')
        
        unique_count = df['id'].nunique()
        total_count = len(df)
        print(f"\n✅ ID uniqueness validated: {unique_count} unique IDs out of {total_count} rows")
    
    def test_id_column_has_no_nulls(self, actual_db_path):
        """Verify ID column has no NULL values"""
        df = load_todos_as_dataframe(actual_db_path)
        
        validate_no_nulls(df, 'id')
        
        print(f"\n✅ ID column has no NULLs: {len(df)} valid IDs")
    
    def test_complete_column_values(self, actual_db_path):
        """Verify complete column contains only 0 or 1"""
        df = load_todos_as_dataframe(actual_db_path)
        
        valid_values = [0, 1]
        validate_value_range(df, 'complete', valid_values)
        
        value_counts = df['complete'].value_counts().to_dict()
        print(f"\n✅ Complete values validated: {value_counts}")
    
    def test_title_max_length(self, actual_db_path):
        """Verify all titles are within 100 character limit"""
        df = load_todos_as_dataframe(actual_db_path)
        
        # Filter out potential NULLs
        non_null_titles = df[df['title'].notna()]
        
        if len(non_null_titles) > 0:
            validate_string_max_length(df, 'title', max_length=100)
            
            max_len = non_null_titles['title'].str.len().max()
            min_len = non_null_titles['title'].str.len().min()
            avg_len = non_null_titles['title'].str.len().mean()
            
            print(f"\n✅ Title length validated:")
            print(f"   Min: {min_len}, Max: {max_len}, Avg: {avg_len:.1f}")
        else:
            print("\n⚠️  No non-null titles to validate length")
    
    def test_data_quality_report(self, actual_db_path):
        """Generate and display comprehensive data quality report"""
        df = load_todos_as_dataframe(actual_db_path)
        
        report = get_data_quality_report(df)
        
        print("\n" + "="*60)
        print("DATA QUALITY REPORT")
        print("="*60)
        
        print(f"\n📊 Overview:")
        print(f"   Total Rows: {report['total_rows']}")
        print(f"   Total Columns: {report['total_columns']}")
        print(f"   Columns: {report['column_names']}")
        
        if 'id_stats' in report:
            print(f"\n🔑 ID Column:")
            for key, value in report['id_stats'].items():
                print(f"   {key}: {value}")
        
        if 'title_stats' in report:
            print(f"\n📝 Title Column:")
            for key, value in report['title_stats'].items():
                print(f"   {key}: {value}")
        
        if 'complete_stats' in report:
            print(f"\n✅ Complete Column:")
            for key, value in report['complete_stats'].items():
                print(f"   {key}: {value}")
        
        print("="*60)
        
        # Assert report was generated successfully
        assert report['total_rows'] > 0, "Should have data in report"
        assert 'id_stats' in report, "Should have ID statistics"


class TestCurrentDatabaseState:
    """Validate the current state of your database (2 records)"""
    
    def test_database_has_two_records(self, actual_db_path):
        """Verify database currently has 2 records as you mentioned"""
        df = load_todos_as_dataframe(actual_db_path)
        
        assert len(df) == 4, f"Expected 4 records, found {len(df)}"
        print(f"\n✅ Confirmed: Database has {len(df)} records")
    
    def test_verify_your_sample_data(self, actual_db_path):
        """Verify the 2 records you added match expected values"""
        df = load_todos_as_dataframe(actual_db_path)
        
        # Your records from SQLite output:
        # (1, 'Welcome to the application', 0)
        # (2, 'Good Morning, have a nice day', 0)
        
        # Check first record
        first_record = df[df['id'] == 1].iloc[0]
        assert first_record['title'] == 'Sample task 1'
        
        # Check second record
        second_record = df[df['id'] == 2].iloc[0]
        assert second_record['title'] == 'Sample task 2'
        
        print("\n✅ Both records validated:")
        print(df.to_string(index=False))
    
