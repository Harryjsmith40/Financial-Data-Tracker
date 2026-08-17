import pandas as pd
import pytest
from pandera.errors import SchemaError

from data_repository import DataRepository
from financial_tracker import FinancialTracker
from Config.config import schema
from schema_validators import input_schema_validator, master_record_validator, accounts_validator

repo = DataRepository()
tracker = FinancialTracker(repo)

master = pd.DataFrame({
    'date': ['01/01/2024', '15/01/2024', '01/02/2024'],
    'amount': [-5000, 10000, -3000],
    'desc': ['Coles', 'Salary', 'Netflix'],
    'balance': [95000, 105000, 102000],
    'account_name': ['CommBank', 'CommBank', 'CommBank'],
    'account_type': ['Current', 'Current', 'Current']
}).astype(schema['dtypes'])

# Overlaps with master on Feb, new data in March
partial_overlap_input = pd.DataFrame({
    'date': ['01/02/2024', '15/03/2024'],
    'amount': [-3000, -8000],
    'desc': ['Netflix', 'Rent'],
    'balance': [102000, 94000],
    'account_name': ['CommBank', 'CommBank'],
    'account_type': ['Current', 'Current']
}).astype(schema['dtypes'])

# Expected result for partial overlap
partial_overlap_correct_result = pd.DataFrame({
    'date': ['15/03/2024'],
    'amount': [-8000],
    'desc': ['Rent'],
    'balance': [94000],
    'account_name': ['CommBank'],
    'account_type': ['Current']
}).astype(schema['dtypes'])

# Entirely new data
no_overlap_input = pd.DataFrame({
    'date': ['01/04/2024'],
    'amount': [-2000],
    'desc': ['Spotify'],
    'balance': [92000],
    'account_name': ['CommBank'],
    'account_type': ['Current']
}).astype(schema['dtypes'])

# Expected result for no overlap
no_overlap_correct_result = pd.DataFrame({
    'date': ['01/04/2024'],
    'amount': [-2000],
    'desc': ['Spotify'],
    'balance': [92000],
    'account_name': ['CommBank'],
    'account_type': ['Current']
}).astype(schema['dtypes'])

# Exact copy of master
full_overlap_input = master.copy()

# Expected result for full overlap
full_overlap_correct_result = pd.DataFrame({
    'date': [],
    'amount': [],
    'desc': [],
    'balance': [],
    'account_name': [],
    'account_type': []
}).astype(schema['dtypes'])

def test_partial_overlap(monkeypatch):
    monkeypatch.setattr(DataRepository, 'read_master', lambda *args, **kwargs: master)
    print(DataRepository.read_master())
    result = tracker.deduplicate(partial_overlap_input)

    pd.testing.assert_frame_equal(result,partial_overlap_correct_result)

def test_no_overlap(monkeypatch):
    monkeypatch.setattr(DataRepository, 'read_master', lambda *args, **kwargs: master)

    result = tracker.deduplicate(no_overlap_input)

    pd.testing.assert_frame_equal(result,no_overlap_correct_result)

def test_full_overlap(monkeypatch):
    monkeypatch.setattr(DataRepository, 'read_master', lambda *args, **kwargs: master)
    
    result = tracker.deduplicate(full_overlap_input)

    pd.testing.assert_frame_equal(result,full_overlap_correct_result, check_dtype=False)

null_df = pd.DataFrame({
    'date': ['01/01/2024'],
    'amount': [None],
    'desc': ['Coles'],
    'balance': [95000]
})

def test_null_input_schema_validator():
    with pytest.raises(SchemaError):
        input_schema_validator.validate(null_df)

master_schema = pd.DataFrame({
    'date': ['01/01/2024', '15/01/2024', '01/02/2024'],
    'amount': [-50.00, 100.00, -30.00],
    'desc': ['Coles', 'Salary', 'Netflix'],
    'balance': [950.00, 1050.00, 1020.00],
    'account_name': ['CommBank', 'CommBank', 'CommBank'],
    'account_type': ['Current', 'Current', 'Current']
}).astype(schema['dtypes'])

def test_master_schema_validator():
    with pytest.raises(SchemaError):
        master_record_validator.validate(master_schema)

accounts_df = pd.DataFrame({
        'account_name': [None],
        'account_type': [1],
        'last_updated': ['01/01/2024']
})

def test_accounts_schema_validator():
    with pytest.raises(SchemaError):
        accounts_validator.validate(accounts_df)

# Read and Clean Testing
# Tests null in all columns where they need to be dropped and tests correct pence conversion
read_and_clean_input = pd.DataFrame({
    'date': ['01/02/2024', '15/03/2024','30/01/2024',None],
    'amount': [-30.00, -80.00, None,50.00],
    'desc': ['Netflix', 'Rent','Error','Haircut'],
    'balance': [1020.00, None, 26.75, 94.16],
})

read_and_clean_input['date'] = pd.to_datetime(read_and_clean_input['date'], format='%d/%m/%Y')

read_and_clean_result = pd.DataFrame({
    'date': ['01/02/2024'],
    'amount': [-3000],
    'desc': ['Netflix'],
    'balance': [102000],
})

read_and_clean_result['date'] = pd.to_datetime(read_and_clean_result['date'], format='%d/%m/%Y')

def test_read_and_clean(monkeypatch):
    monkeypatch.setattr(DataRepository, 'read_input_CSV', lambda *args, **kwargs: read_and_clean_input)
    
    result = tracker.read_and_clean('dummy_path.csv')

    pd.testing.assert_frame_equal(result,read_and_clean_result, check_dtype=True)