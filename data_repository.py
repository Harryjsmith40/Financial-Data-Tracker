from Config.config import master_record_path, account_info_path, schema

import logging
import pandas as pd

class DataRepository():
    '''Handles all data file interactions - while class is not strictly needed at this stage is exists for when a DB is implemented'''
    schema = schema

    @staticmethod
    def read_master():
        '''Reads the master file'''
        master_record = pd.read_csv(master_record_path, dtype=schema['dtypes'], parse_dates=schema['date_columns'], date_format=schema['date_format'])
        return master_record

    @staticmethod
    def append_master(df):
        '''Updates master_record.csv to include new data'''
        # Appends to master_record.csv the new data
        df.to_csv(master_record_path, mode='a', header=False, index=False, date_format=schema['date_format'])
        logging.info('Successfully appended to master')

    @staticmethod
    def create_master(master_record):
        master_record.to_csv(master_record_path, index=False)
        logging.info('Successfully writen to master')

    @staticmethod
    def read_account():
        '''Reads the accounts CSV into a dataframe'''
        account_info = pd.read_csv(account_info_path)
        return account_info
    
    @staticmethod
    def update_timestamp(selection, account_info):
        # Updated the last updated timestamp on the accounts CSV
        account_info.loc[selection,'Last Updated'] = str(pd.Timestamp.now())
        account_info.to_csv(account_info_path, index=False)
        logging.info('Timestamp successfully updated')

    @staticmethod
    def create_account(account_name, account_type):
        '''Creates a new account in the account file'''
        new_account_info = pd.DataFrame({'Account Name': [account_name], 'Account Type': [account_type], 'Last Updated': [pd.Timestamp.now()]})
        new_account_info.to_csv(account_info_path, mode='a', header=False, index=False)

    @staticmethod
    def write_account():
            '''Creates the accounts file when it doesn't exist'''
            account_info_df = pd.DataFrame(columns=['Account Name', 'Account Type', 'Last Updated'])
            account_info = account_info_df.to_csv(account_info_path, index=False)
            return account_info_df


    @staticmethod
    def read_input_CSV(file_path):
        df = pd.read_csv(file_path, names=['Date', 'Amount', 'Desc', 'Balance'], header=None, dtype=schema['input_dtypes'], parse_dates=schema['date_columns'], date_format=schema['date_format'])
        return df