from Config.config import data_folder, master_record_path, account_info_path
from data_repository import DataRepository
from schema_validators import input_schema_validator
from financial_base import FinancialBase

import os
import pandas as pd
import logging
from decimal import Decimal

class FinancialTracker(FinancialBase):
    '''A finnacial tracker designed to help make inform make data based decisions'''    

    def __init__(self):
        '''Initialises the master record and accounts CSVs'''

        # Inherits the schema from the base class, FinancialBase
        super().__init__()


        # Checking if the master file exists
        # Currently assumes ./Data/ exists if the user doesn't have ./Data/master_record.csv 
        if os.path.exists(master_record_path):
            # Checks structure of file is correct
            master_record = DataRepository.read_master()
            if master_record.columns.tolist() == ['Date', 'Amount', 'Desc', 'Balance', 'Account Name', 'Account Type']:
                logging.info('master_record initialised correctly')
            else: 
                logging.error('master_record exists with incorrect headers')
                raise ValueError('master_record exists with incorrect headers')

        # Creates it if it doesn't exist
        else:
            master_record = pd.DataFrame(columns=['Date', 'Amount', 'Desc', 'Balance', 'Account Name', 'Account Type'])
            if os.path.exists(data_folder):
                DataRepository.create_master(master_record)
            else:
                os.mkdir(data_folder)
                DataRepository.create_master(master_record)

        # Checks to see if the accounts CSV exists
        if os.path.exists(account_info_path):
            self.account_info = DataRepository.read_account()
            if self.account_info.columns.tolist() == ['Account Name', 'Account Type', 'Last Updated']:
                logging.info('account_info initialised correctly')

        # Creates the account CSV if it doesn't
        else:
            self.account_info = DataRepository.write_account()

    @staticmethod
    def read_and_clean(file_path):
        '''Reads CSV files, formates dates and data types, removes null data and adds an index'''
        # Read the CSV file into a DataFrame
        df = DataRepository.read_input_CSV(file_path)
        # Drops na values if the amount or date or balance is missing
        df.dropna(subset=['Date','Amount','Balance'], inplace=True)

        # Converts columns to pence based logic to avoid floating point errors
        df['Balance'] = df['Balance'].apply(lambda x: int(Decimal(str(x)) * 100))
        df['Amount'] = df['Amount'].apply(lambda x: int(Decimal(str(x)) * 100))

        # Used to preserve intra-day transaction order from original export as resolution is 1 days but original export hold order of transactions within the day
        df.insert(0, 'Transaction Order', range(1, len(df) + 1))

        # Sort by date to maintain chronological order - Transaction Order descending as bank exports are reverse chronological
        df.sort_values(by=['Date', 'Transaction Order'], inplace=True, ascending=[True, False])
        
        # Drops column in order to preserve simplifed file
        df.drop(columns=['Transaction Order'], inplace=True)

        df = input_schema_validator.validate(df)

        return df
    
    @staticmethod
    def deduplicate(cleaned_input):
        ''' Checks for and removes duplicates''' 
        master_record = DataRepository.read_master()
        # Left merge master and input together
        merged_df = cleaned_input.merge(master_record, how='left', on=['Date', 'Amount', 'Desc', 'Balance', 'Account Name', 'Account Type'], indicator=True)
        # Drops all but the things existing in the input only
        merged_df = merged_df[merged_df['_merge'] == 'left_only']
        # drops the extra column that indicates the merge origins
        merged_df = merged_df.drop(labels='_merge' , axis='columns')
        # reindex the data frame as input data holds original indexs after drop
        merged_df = merged_df.reset_index(drop=True)

        return merged_df

    def select_account(self):
        
        while True:
            # Iteractively prints the account names from account csvand types for the user to select from
            for index, row in self.account_info.iterrows():
                print(index, row['Account Name'])
            print('A Add New Account')
            print('B Back to main menu')

            account_name_option = input('Please provide the number/letter of the account this data is from: ')

            # Creates new account
            if account_name_option.upper() == 'A':
                # User provides account name and type
                account_name = input('Please provide the name of the account this data is from: ')
                account_type = input('Please provide the type of this account (e.g. current, savings, credit card): ')

                DataRepository.create_account(account_name, account_type)

                return account_name, account_type
            
            # Goes back to main menu
            elif account_name_option.upper() == 'B':
                break
            
            else:
                # Checks if selected option is a valid account number 
                try:
                    selection = int(account_name_option)
                except ValueError:
                    print('Invalid input please try again')
                    logging.info('Select account - Invalid input please try again')
                    continue

                # Checks if number falls within the range of existing accounts
                if selection < len(self.account_info):
                    account_info = DataRepository.read_account()
                    # Reads the account details and returns them
                    account_name = account_info.loc[selection, 'Account Name']
                    account_type = account_info.loc[selection, 'Account Type']

                    # Updates the timestamp of the account updated to
                    DataRepository.update_timestamp(selection, account_info)

                    return account_name, account_type

                # Fall back for invalid input
                else:
                    print('Invalid input please try again')
                    logging.error('Select account - Invalid input please try again')

    def upload_file(self):
        '''Prompts the user for the file name'''
        
        while True:
            print('B Back to main menu')
            file_path_option = input('Please ensure the CSV file is in the data folder and provide the file name would like to upload: ')

            # Sends user back to main menu if selected
            if file_path_option.upper() == 'B':
                break
            
            # Uses the schema file paths to create the full file path for the CSV
            file_path = os.path.join(data_folder, file_path_option)

            # Checks if the provided file/path exists
            if os.path.exists(file_path):
                cleaned_input = self.read_and_clean(file_path)
                logging.info('file_path exists correctly')

                # Handles case where user goes back to menu rather than continues
                result = self.select_account()
                if result is None:
                    return
                
                # Assigns the account details for uploading to master
                account_name, account_type = result
                cleaned_input['Account Name'] = account_name
                cleaned_input['Account Type'] = account_type

                # Checks and removes duplicates from the uploaded file
                deduplicated_input = self.deduplicate(cleaned_input)
                
                # Writes the uploaded file to the master record
                DataRepository.append_master(deduplicated_input)

            # Raises issue if file doesn't exist
            else:
                logging.error('Failed file does not exist')
                print('Upload file - Failed file does not exist')