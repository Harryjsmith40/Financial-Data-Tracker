import pandas as pd
import pytest
from pandera.errors import SchemaError

from data_repository import DataRepository
from financial_tracker import FinancialTracker
from Config.config import schema
from schema_validators import input_schema_validator, master_record_validator, accounts_validator

master = pd.DataFrame({
    'Date': ['01/01/2024', '15/01/2024', '01/02/2024'],
    'Amount': [-5000, 10000, -3000],
    'Desc': ['Coles', 'Salary', 'Netflix'],
    'Balance': [95000, 105000, 102000],
    'Account Name': ['CommBank', 'CommBank', 'CommBank'],
    'Account Type': ['Current', 'Current', 'Current']
}).astype(schema['dtypes'])

# Overlaps with master on Feb, new data in March
partial_overlap_input = pd.DataFrame({
    'Date': ['01/02/2024', '15/03/2024'],
    'Amount': [-3000, -8000],
    'Desc': ['Netflix', 'Rent'],
    'Balance': [102000, 94000],
    'Account Name': ['CommBank', 'CommBank'],
    'Account Type': ['Current', 'Current']
}).astype(schema['dtypes'])

# Expected result for partial overlap
partial_overlap_correct_result = pd.DataFrame({
    'Date': ['15/03/2024'],
    'Amount': [-8000],
    'Desc': ['Rent'],
    'Balance': [94000],
    'Account Name': ['CommBank'],
    'Account Type': ['Current']
}).astype(schema['dtypes'])

# Entirely new data
no_overlap_input = pd.DataFrame({
    'Date': ['01/04/2024'],
    'Amount': [-2000],
    'Desc': ['Spotify'],
    'Balance': [92000],
    'Account Name': ['CommBank'],
    'Account Type': ['Current']
}).astype(schema['dtypes'])

# Expected result for no overlap
no_overlap_correct_result = pd.DataFrame({
    'Date': ['01/04/2024'],
    'Amount': [-2000],
    'Desc': ['Spotify'],
    'Balance': [92000],
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
}).astype(schema['dtypes'])

def test_partial_overlap(monkeypatch):
    monkeypatch.setattr(DataRepository, 'read_master', lambda *args, **kwargs: master)
    
    result = FinancialTracker.deduplicate(partial_overlap_input)

    pd.testing.assert_frame_equal(result,partial_overlap_correct_result)

def test_no_overlap(monkeypatch):
    monkeypatch.setattr(DataRepository, 'read_master', lambda *args, **kwargs: master)

    result = FinancialTracker.deduplicate(no_overlap_input)

    pd.testing.assert_frame_equal(result,no_overlap_correct_result)

def test_full_overlap(monkeypatch):
    monkeypatch.setattr(DataRepository, 'read_master', lambda *args, **kwargs: master)
    
    result = FinancialTracker.deduplicate(full_overlap_input)

    pd.testing.assert_frame_equal(result,full_overlap_correct_result, check_dtype=False)

null_df = pd.DataFrame({
    'Date': ['01/01/2024'],
    'Amount': [None],
    'Desc': ['Coles'],
    'Balance': [95000]
})

def test_null_input_schema_validator():
    with pytest.raises(SchemaError):
        input_schema_validator.validate(null_df)

master = pd.DataFrame({
    'Date': ['01/01/2024', '15/01/2024', '01/02/2024'],
    'Amount': [-50.00, 100.00, -30.00],
    'Desc': ['Coles', 'Salary', 'Netflix'],
    'Balance': [950.00, 1050.00, 1020.00],
    'Account Name': ['CommBank', 'CommBank', 'CommBank'],
    'Account Type': ['Current', 'Current', 'Current']
}).astype(schema['dtypes'])

def test_master_schema_validator():
    with pytest.raises(SchemaError):
        master_record_validator.validate(master)

accounts_df = pd.DataFrame({
        'Account Name': [None],
        'Account Type': [1],
        'Last Updated': ['01/01/2024']
})

def test_accounts_schema_validator():
    with pytest.raises(SchemaError):
        accounts_validator.validate(accounts_df)

# Read and Clean Testing
# Tests null in all columns where they need to be dropped and tests correct pence conversion
read_and_clean_input = pd.DataFrame({
    'Date': ['01/02/2024', '15/03/2024','30/01/2024',None],
    'Amount': [-30.00, -80.00, None,50.00],
    'Desc': ['Netflix', 'Rent','Error','Haircut'],
    'Balance': [1020.00, None, 26.75, 94.16],
})

read_and_clean_input['Date'] = pd.to_datetime(read_and_clean_input['Date'], format='%d/%m/%Y')s

read_and_clean_result = pd.DataFrame({
    'Date': ['01/02/2024'],
    'Amount': [-3000],
    'Desc': ['Netflix'],
    'Balance': [102000],
})

read_and_clean_result['Date'] = pd.to_datetime(read_and_clean_result['Date'], format='%d/%m/%Y')

def test_read_and_clean(monkeypatch):
    monkeypatch.setattr(DataRepository, 'read_input_CSV', lambda file_path: read_and_clean_input)
    
    result = FinancialTracker.read_and_clean('dummy_path.csv')

    pd.testing.assert_frame_equal(result,read_and_clean_result, check_dtype=True)