from Config.config import schema
from schema_validators import input_schema_validator, master_record_validator, accounts_validator

import logging
import pandas as pd
import duckdb
import pandera as pa

class DataRepository:
    '''Handles all data file interactions - while class is not strictly needed at this stage exists for when a DB is implemented'''
    def __init__(self):
        import os
        os.makedirs("Data", exist_ok=True)
        self.con = duckdb.connect("Data/data_base.db")
        self.schema = schema
        self._ensure_tables_exist()

    def read_master(self):
        '''Reads the master file'''
        master_record = self.con.sql("SELECT * FROM master").df().set_index("master_id")
        return master_record

    def append_master(self, df):
        '''Updates master_record.csv to include new data'''
        # Validates Data Structure
        try:
            validated_df = master_record_validator.validate(df)
        except pa.errors.SchemaError as exc:
            logging.error(f'Master record validation failed: {exc}')
            raise
        # Appends to master_record.csv the new data
        self.con.sql("INSERT INTO master (amount, date, \"desc\", balance, account_name, account_type) SELECT amount, date, \"desc\", balance, account_name, account_type FROM validated_df")
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
        # Creates the df
        df = pd.DataFrame({'account_name': [account_name],
                           'account_type':[account_type],
                           'last_updated':[pd.Timestamp.now()]})
        # Validates Data Structure
        try:
            validated_df = accounts_validator.validate(df)
        except pa.errors.SchemaError as exc:
            logging.error(f'Account details validation failed: {exc}')
            raise
        # Appends to the accounts table
        self.con.sql("INSERT INTO accounts (account_name, account_type, last_updated) SELECT account_name, account_type, last_updated FROM validated_df;"),

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
        # Read ipnut file
        df = pd.read_csv(file_path, names=['date', 'amount', 'desc', 'balance'], header=None, dtype=self.schema['input_dtypes'], parse_dates=schema['date_columns'], date_format=schema['date_format'])
        # Validate the df generated from the input
        try:
            validated_df = input_schema_validator.validate(df)
        except pa.errors.SchemaError as exc:
            logging.error(f'Input file details validation failed: {exc}')
            raise
        return validated_df 

    def read_daily_net_worth(self):
        daily_net_worth = self.con.sql("""
            WITH step1 AS (
                SELECT 
                    account_name,
                    account_type,
                    date,
                    balance
                FROM master m1
                WHERE master_id = (
                    SELECT MAX(master_id)
                    FROM master m2 
                    WHERE m1.account_name = m2.account_name
                    AND m1.account_type = m2.account_type
                    AND m1.date = m2.date
                )
                ORDER BY date
            ),
            date_spine AS (
                SELECT *
                FROM GENERATE_SERIES(
                    (SELECT MIN(date) FROM master), 
                    CAST(CURRENT_DATE AS DATETIME),
                    INTERVAL 1 DAY
                ) 
            ),
            accounts AS (
                SELECT DISTINCT account_name, account_type
                FROM master
            ),
            joined AS (
                SELECT 
                    d.generate_series AS day,
                    a.account_name,
                    a.account_type,
                    s.balance
                FROM date_spine d 
                CROSS JOIN accounts a
                LEFT JOIN step1 s ON d.generate_series = s.date
                AND a.account_name = s.account_name
                AND a.account_type = s.account_type
                ORDER BY d.generate_series
            ),
            filled AS (
                SELECT 
                    day,
                    account_name,
                    account_type,
                    LAST_VALUE(balance IGNORE NULLS) OVER (
                        PARTITION BY account_name, account_type
                        ORDER BY day
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) AS balance
                FROM joined
            )
            SELECT day, SUM(balance) AS net_worth
            FROM filled
            GROUP BY day
            ORDER BY day
        """).df().set_index("day")
        return daily_net_worth