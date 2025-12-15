"""Pandas DataFrame helpers for data validation"""
import pandas as pd
import sqlite3
from pathlib import Path


def load_todos_as_dataframe(db_path):
    """
    Load entire todo table into pandas DataFrame
    
    Args:
        db_path: Path to SQLite database
    
    Returns:
        pandas.DataFrame with todo data
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM todo ORDER BY id", conn)
    conn.close()
    return df


def validate_schema(df, expected_columns):
    """
    Validate DataFrame has expected columns in correct order
    
    Args:
        df: pandas DataFrame
        expected_columns: List of expected column names
    
    Returns:
        bool: True if schema matches
    
    Raises:
        AssertionError if schema doesn't match
    """
    actual_columns = list(df.columns)
    assert actual_columns == expected_columns, (
        f"Schema mismatch! Expected: {expected_columns}, Got: {actual_columns}"
    )
    return True


def validate_column_types(df, expected_types):
    """
    Validate DataFrame column data types
    
    Args:
        df: pandas DataFrame
        expected_types: Dict mapping column names to expected dtypes
    
    Returns:
        bool: True if all types match
    """
    for col, expected_dtype in expected_types.items():
        actual_dtype = df[col].dtype
        assert actual_dtype == expected_dtype, (
            f"Column '{col}' type mismatch! Expected: {expected_dtype}, Got: {actual_dtype}"
        )
    return True


def validate_no_nulls(df, column):
    """
    Assert column has no NULL values
    
    Args:
        df: pandas DataFrame
        column: Column name to check
    
    Returns:
        bool: True if no nulls found
    """
    null_count = df[column].isnull().sum()
    assert null_count == 0, f"Column '{column}' has {null_count} NULL values"
    return True


def validate_unique(df, column):
    """
    Assert column values are unique (no duplicates)
    
    Args:
        df: pandas DataFrame
        column: Column name to check
    
    Returns:
        bool: True if all values unique
    """
    unique_count = df[column].nunique()
    total_count = len(df)
    assert unique_count == total_count, (
        f"Column '{column}' has duplicates! Unique: {unique_count}, Total: {total_count}"
    )
    return True


def validate_value_range(df, column, valid_values):
    """
    Assert column contains only values from valid set
    
    Args:
        df: pandas DataFrame
        column: Column name to check
        valid_values: List or set of valid values
    
    Returns:
        bool: True if all values valid
    """
    invalid_mask = ~df[column].isin(valid_values)
    invalid_count = invalid_mask.sum()
    
    if invalid_count > 0:
        invalid_values = df.loc[invalid_mask, column].unique()
        raise AssertionError(
            f"Column '{column}' has {invalid_count} invalid values: {invalid_values}. "
            f"Valid values: {valid_values}"
        )
    return True


def validate_string_max_length(df, column, max_length):
    """
    Assert all string values in column are within max length
    
    Args:
        df: pandas DataFrame
        column: Column name to check
        max_length: Maximum allowed length
    
    Returns:
        bool: True if all values within limit
    """
    # Filter out NULLs before checking length
    non_null_df = df[df[column].notna()]
    
    if len(non_null_df) == 0:
        return True  # No data to validate
    
    lengths = non_null_df[column].str.len()
    max_found = lengths.max()
    
    assert max_found <= max_length, (
        f"Column '{column}' has values exceeding max length {max_length}. "
        f"Longest value: {max_found} characters"
    )
    return True


def get_data_quality_report(df):
    """
    Generate comprehensive data quality summary
    
    Args:
        df: pandas DataFrame
    
    Returns:
        dict: Data quality metrics
    """
    report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'column_names': list(df.columns),
    }
    
    # ID column analysis
    if 'id' in df.columns:
        report['id_stats'] = {
            'min': int(df['id'].min()) if len(df) > 0 else None,
            'max': int(df['id'].max()) if len(df) > 0 else None,
            'unique_count': int(df['id'].nunique()),
            'has_nulls': bool(df['id'].isnull().any()),
            'has_duplicates': bool(df['id'].duplicated().any())
        }
    
    # Title column analysis
    if 'title' in df.columns:
        report['title_stats'] = {
            'null_count': int(df['title'].isnull().sum()),
            'empty_string_count': int((df['title'] == '').sum()),
            'whitespace_only_count': int(df['title'].str.strip().eq('').sum()),
            'duplicate_count': int(df['title'].duplicated().sum()),
            'min_length': int(df['title'].str.len().min()) if len(df) > 0 else None,
            'max_length': int(df['title'].str.len().max()) if len(df) > 0 else None,
            'avg_length': float(df['title'].str.len().mean()) if len(df) > 0 else None,
        }
    
    # Complete column analysis
    if 'complete' in df.columns:
        report['complete_stats'] = {
            'value_counts': df['complete'].value_counts().to_dict(),
            'null_count': int(df['complete'].isnull().sum()),
            'unique_values': sorted(df['complete'].unique().tolist())
        }
    
    return report


def find_empty_titles(df):
    """
    Find rows with empty or whitespace-only titles
    
    Args:
        df: pandas DataFrame
    
    Returns:
        pandas.DataFrame: Rows with problematic titles
    """
    empty_mask = (df['title'] == '') | (df['title'].str.strip() == '')
    return df[empty_mask]


def find_null_titles(df):
    """
    Find rows with NULL titles
    
    Args:
        df: pandas DataFrame
    
    Returns:
        pandas.DataFrame: Rows with NULL titles
    """
    return df[df['title'].isnull()]


def find_long_titles(df, threshold=100):
    """
    Find rows with titles exceeding length threshold
    
    Args:
        df: pandas DataFrame
        threshold: Length threshold (default 100)
    
    Returns:
        pandas.DataFrame: Rows with long titles
    """
    long_mask = df['title'].str.len() > threshold
    return df[long_mask]


def find_special_characters(df, pattern='[<>]'):
    """
    Find titles containing special characters
    
    Args:
        df: pandas DataFrame
        pattern: Regex pattern to search for
    
    Returns:
        pandas.DataFrame: Rows matching pattern
    """
    matches = df['title'].str.contains(pattern, na=False, regex=True)
    return df[matches]


def compare_dataframes(df1, df2, key_column='id'):
    """
    Compare two DataFrames and report differences
    
    Args:
        df1: First DataFrame (e.g., before state)
        df2: Second DataFrame (e.g., after state)
        key_column: Column to use as key for comparison
    
    Returns:
        dict: Comparison results
    """
    comparison = {
        'rows_in_df1_only': len(df1[~df1[key_column].isin(df2[key_column])]),
        'rows_in_df2_only': len(df2[~df2[key_column].isin(df1[key_column])]),
        'common_rows': len(df1[df1[key_column].isin(df2[key_column])]),
        'df1_row_count': len(df1),
        'df2_row_count': len(df2),
        'row_count_diff': len(df2) - len(df1)
    }
    
    return comparison