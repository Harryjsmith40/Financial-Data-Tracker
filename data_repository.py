from Config.config import schema
from financial_base import FinancialBase

import logging
import pandas as pd
import duckdb

class DataRepository:
    '''Handles all data file interactions - while class is not strictly needed at this stage is exists for when a DB is implemented'''
    def __init__(self):
        self.con = duckdb.connect("Data/data_base.db")
        self.schema = schema
        self._ensure_tables_exist()

    def read_master(self):
        '''Reads the master file'''
        master_record = self.con.sql("SELECT * FROM master").df().set_index("master_id")
        return master_record

    def append_master(self, df):
        '''Updates master_record.csv to include new data'''
        # Appends to master_record.csv the new data
        self.con.sql("INSERT INTO master (amount, date, \"desc\", balance, account_name, account_type) SELECT amount, date, \"desc\", balance, account_name, account_type FROM df")
        logging.info('Successfully appended to master')

    def read_accounts(self):
        '''Reads the accounts CSV into a dataframe'''
        account_info = self.con.sql("SELECT * FROM accounts").df().set_index("account_id")
        return account_info
    
    def update_timestamp(self, selection):
        # Updated the last updated timestamp on the accounts CSV
        self.con.sql("UPDATE accounts SET last_updated = current_timestamp WHERE account_id = ?", params=[selection])
        logging.info('Timestamp successfully updated')

    def create_account(self, account_name, account_type):
        '''Creates a new account in the account table'''
        self.con.sql("INSERT INTO accounts VALUES (nextval('accounts_id_sequence'),?,?,current_timestamp);",
        params=[account_name,account_type])

    def _ensure_tables_exist(self):
        if not self._table_exists('accounts'):
            self.con.execute("CREATE SEQUENCE accounts_id_sequence START 1; CREATE TABLE accounts (\"account_id\" INTEGER PRIMARY KEY DEFAULT nextval('accounts_id_sequence'),\"account_name\" VARCHAR,\"account_type\" VARCHAR,\"last_updated\" TIMESTAMP);")
        if not self._table_exists('master'):
            self.con.execute("CREATE SEQUENCE master_id_sequence START 1; CREATE TABLE master (\"master_id\" INTEGER PRIMARY KEY DEFAULT nextval('master_id_sequence'),\"date\" TIMESTAMP, \"amount\" INTEGER,\"desc\" VARCHAR,\"balance\" INTEGER,\"account_name\" VARCHAR,\"account_type\" VARCHAR)")

    def _table_exists(self, table_name):
        # Checks that the table exists via the database
        result = self.con.sql(
            "SELECT table_name FROM information_schema.tables WHERE table_name = ?",
            params=[table_name]
        ).fetchall()
        return len(result) > 0

    def read_input_CSV(self, file_path):
        df = pd.read_csv(file_path, names=['date', 'amount', 'desc', 'balance'], header=None, dtype=self.schema['input_dtypes'], parse_dates=schema['date_columns'], date_format=schema['date_format'])
        return df