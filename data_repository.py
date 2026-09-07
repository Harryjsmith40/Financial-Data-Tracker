from Config.config import schema
from schema_validators import input_schema_validator, master_record_validator, accounts_validator
from financial_tracker import FinancialTracker

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
        self.migrate_account_ids()

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
        self.con.sql("INSERT INTO master (amount, date, \"desc\", balance, account_name, account_type) SELECT amount, date, \"desc\", balance, account_id FROM validated_df")
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

        # Finds the new account_id
        account_id = self.con.execute("""
            SELECT account_id
            FROM accounts
            WHERE account_name = ?
            AND account_type = ?
        """, [account_name, account_type]).fetchone()[0]

        return account_id

    def _ensure_tables_exist(self):
        if not self._table_exists('accounts'):
            self.con.execute("CREATE SEQUENCE accounts_id_sequence START 1; CREATE TABLE accounts (\"account_id\" INTEGER PRIMARY KEY DEFAULT nextval('accounts_id_sequence'),\"account_name\" VARCHAR,\"account_type\" VARCHAR,\"last_updated\" TIMESTAMP);")
        if not self._table_exists('master'):
            self.con.execute("CREATE SEQUENCE master_id_sequence START 1; CREATE TABLE master (\"master_id\" INTEGER PRIMARY KEY DEFAULT nextval('master_id_sequence'),\"date\" TIMESTAMP, \"amount\" INTEGER,\"desc\" VARCHAR,\"balance\" INTEGER,\"account_id\" INTEGER)")

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
                    account_id,
                    date,
                    balance
                FROM master m1
                WHERE master_id = (
                    SELECT MAX(master_id)
                    FROM master m2 
                    WHERE m1.account_id = m2.account_id
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
                SELECT DISTINCT account_id
                FROM master
            ),
            joined AS (
                SELECT 
                    d.generate_series AS day,
                    a.account_id,
                    s.balance
                FROM date_spine d 
                CROSS JOIN accounts a
                LEFT JOIN step1 s ON d.generate_series = s.date
                AND a.account_id = s.account_id
                ORDER BY d.generate_series
            ),
            filled AS (
                SELECT 
                    day,
                    account_id,
                    LAST_VALUE(balance IGNORE NULLS) OVER (
                        PARTITION BY account_id
                        ORDER BY day
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) AS balance
                FROM joined
            )
            SELECT day, SUM(balance) AS net_worth
            FROM filled
            GROUP BY day
            ORDER BY day;
        """).df().set_index("day")
        return daily_net_worth
    
    def migrate_account_ids(self):
        # Pulls the master table headers
        master_columns = self.con.sql("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'master';").df()

        # Converts the query from a single column contains the header names to a set
        master_column_names = set(master_columns["column_name"])

        # Legacy column namse
        required_columns = {"account_name", "account_type"}

        # Checks for legacy headers and return if not found
        if not required_columns.issubset(master_column_names):
            return
        
        # Run conversion logic
        self.con.sql("UPDATE master AS m SET account_id = a.account_id FROM accounts AS a WHERE m.account_type = a.account_type AND m.account_name = a.account_name;")

        # Check all transactions were correctly assigned an account
        unmatched_transactions = self.con.sql("SELECT DISTINCT account_name, account_type FROM master WHERE account_id IS NULL;").df()

        # Returns if no unmatched transactions remain
        if not unmatched_transactions.empty:
            
            # Goes through each row in the unmatched transactions and uses select_account in order to either create a new one for it or assign to a pre-existing account
            for row in unmatched_transactions.itertuples(index=False):
                print(row.account_name)
                print(row.account_type)

                account_id = None

                # Handles the case where the users goes back in the account selection
                while account_id is None:
                    account_id  = FinancialTracker.select_account()

                    if account_id is None:
                        print("Please do not skip account assignment")
                
                # Updates the master with the newly given account_id
                self.con.execute("""
                    UPDATE master
                    SET account_id = ?
                    WHERE account_id IS NULL
                    AND account_name = ?
                    AND account_type = ?
                """, [account_id, row.account_name, row.account_type])

            # Deleted legacy rows
            self.con.execute("ALTER TABLE master DROP COLUMN account_name")
            self.con.execute("ALTER TABLE master DROP COLUMN account_type")