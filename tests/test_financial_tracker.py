import pandas as pd
import pytest
from pandera.errors import SchemaError

from data_repository import DataRepository
from financial_tracker import FinancialTracker
from Config.config import schema
from schema_validators import input_schema_validator

master = pd.DataFrame({
    'Date': ['01/01/2024', '15/01/2024', '01/02/2024'],
    'Amount': [-50.00, 100.00, -30.00],
    'Desc': ['Coles', 'Salary', 'Netflix'],
    'Balance': [950.00, 1050.00, 1020.00],
    'Account Name': ['CommBank', 'CommBank', 'CommBank'],
    'Account Type': ['Current', 'Current', 'Current']
}).astype(schema['dtypes'])

# Overlaps with master on Feb, new data in March
partial_overlap_input = pd.DataFrame({
    'Date': ['01/02/2024', '15/03/2024'],
    'Amount': [-30.00, -80.00],
    'Desc': ['Netflix', 'Rent'],
    'Balance': [1020.00, 940.00],
    'Account Name': ['CommBank', 'CommBank'],
    'Account Type': ['Current', 'Current']
}).astype(schema['dtypes'])

# Expected result for partial overlap
partial_overlap_correct_result = pd.DataFrame({
    'Date': ['15/03/2024'],
    'Amount': [-80.00],
    'Desc': ['Rent'],
    'Balance': [940.00],
    'Account Name': ['CommBank'],
    'Account Type': ['Current']
}).astype(schema['dtypes'])

# Entirely new data
no_overlap_input = pd.DataFrame({
    'Date': ['01/04/2024'],
    'Amount': [-20.00],
    'Desc': ['Spotify'],
    'Balance': [920.00],
    'Account Name': ['CommBank'],
    'Account Type': ['Current']
}).astype(schema['dtypes'])

# Expected result for no overlap
no_overlap_correct_result = pd.DataFrame({
    'Date': ['01/04/2024'],
    'Amount': [-20.00],
    'Desc': ['Spotify'],
    'Balance': [920.00],
    'Account Name': ['CommBank'],
    'Account Type': ['Current']
}).astype(schema['dtypes'])

# Exact copy of master
full_overlap_input = master.copy()

# Expected result for full overlap
full_overlap_correct_result = pd.DataFrame({
    'Date': [],
    'Amount': [],
    'Desc': [],
    'Balance': [],
    'Account Name': [],
    'Account Type': []
})

def test_partial_overlap(monkeypatch):
    monkeypatch.setattr(DataRepository, 'read_master', lambda: master)
    
    result = FinancialTracker.deduplicate(partial_overlap_input)

    pd.testing.assert_frame_equal(result,partial_overlap_correct_result)

def test_no_overlap(monkeypatch):
    monkeypatch.setattr(DataRepository, 'read_master', lambda: master)

    result = FinancialTracker.deduplicate(no_overlap_input)

    pd.testing.assert_frame_equal(result,no_overlap_correct_result)

def test_full_overlap(monkeypatch):
    monkeypatch.setattr(DataRepository, 'read_master', lambda: master)
    
    result = FinancialTracker.deduplicate(full_overlap_input)

    pd.testing.assert_frame_equal(result,full_overlap_correct_result, check_dtype=False)

null_df = pd.DataFrame({
    'Date': ['01/01/2024'],
    'Amount': [None],
    'Desc': ['Coles'],
    'Balance': [950.00]
})

def test_null_input_schema_validator():
    with pytest.raises(SchemaError):
        input_schema_validator.validate(null_df)