from Config.config import data_folder, schema
from schema_validators import input_schema_validator

import os
import pandas as pd
import logging
from decimal import Decimal

class FinancialTracker:
    '''A finacial tracker designed to help make inform make data based decisions'''    

    def __init__(self, repo):
        '''Initialises the master record and accounts CSVs'''
        # Inherits the schema from the base class, FinancialBase
        self.repo = repo
        self.schema = schema

    def read_and_clean(self, file_path):
        '''Reads CSV files, formates dates and data types, removes null data and adds an index'''
        # Read the CSV file into a DataFrame
        df = self.repo.read_input_CSV(file_path)
        # Drops na values if the amount or date or balance is missing
        df.dropna(subset=['date','amount','balance'], inplace=True)

        # Converts columns to pence based logic to avoid floating point errors
        df['balance'] = df['balance'].apply(lambda x: int(Decimal(str(x)) * 100))
        df['amount'] = df['amount'].apply(lambda x: int(Decimal(str(x)) * 100))

        # Used to preserve intra-day transaction order from original export as resolution is 1 days but original export hold order of transactions within the day
        df.insert(0, 'Transaction Order', range(1, len(df) + 1))

        # Sort by date to maintain chronological order - Transaction Order descending as bank exports are reverse chronological
        df.sort_values(by=['date', 'Transaction Order'], inplace=True, ascending=[True, False])
        
        # Drops column in order to preserve simplifed file
        df.drop(columns=['Transaction Order'], inplace=True)

        df = input_schema_validator.validate(df)

        return df
    
    def deduplicate(self, cleaned_input):
        ''' Checks for and removes duplicates''' 
        master_record = self.repo.read_master()
        # Left merge master and input together
        merged_df = cleaned_input.merge(master_record, how='left', on=['date', 'amount', 'desc', 'balance', 'account_name', 'account_type'], indicator=True)
        # Drops all but the things existing in the input only
        merged_df = merged_df[merged_df['_merge'] == 'left_only']
        # drops the extra column that indicates the merge origins
        merged_df = merged_df.drop(labels='_merge' , axis='columns')
        # reindex the data frame as input data holds original indexs after drop
        merged_df = merged_df.reset_index(drop=True)

        return merged_df

    def select_account(self, type="normal"):
        
        while True:
            # Iteractively prints the account names from account csv and types for the user to select from
            accounts = self.repo.read_accounts()

            print(accounts)


            # Allows code to be used to select account to delete
            if type == "normal":
                print('A Add New Account')
            print('B Back to main menu')

            account_name_option = input('Please provide the account_id of the account this data is from: ')

            # Creates new account
            if type == "normal":
                if account_name_option.upper() == 'A':
                    # User provides account name and type
                    account_name = input('Please provide the name of the account this data is from: ')
                    account_type = input('Please provide the type of this account (e.g. current, savings, credit card): ')

                    account_id = self.repo.create_account(account_name, account_type)

                    return account_id
            
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
                if selection < len(accounts)+1:
                    # Updates the timestamp of the account updated to
                    self.repo.update_timestamp(selection)
                    # Returns account_id
                    return int(selection)

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
                account_id = result
                cleaned_input['account_id'] = account_id

                # Checks and removes duplicates from the uploaded file
                deduplicated_input = self.deduplicate(cleaned_input)
                
                # Writes the uploaded file to the master record
                self.repo.append_master(deduplicated_input)

            # Raises issue if file doesn't exist
            else:
                logging.error('Failed file does not exist')
                print('Upload file - Failed file does not exist')

    def account_management_menu(self):
        
        while True:
            print("Please choose your management operation: ")
            print("A - Upload a file")
            print("B - Delete an account")
            print("C - Back to main menu")

            selection = input("")

            if selection.upper() == "A":
                self.upload_file()
            elif selection.upper() == "B":
                # Prompts user for account to delete
                account_id = self.select_account(type="Delete")
                self.repo.delete_account(account_id)
            elif selection.upper() == "C":
                break
            else:
                print('Invalid input please try again')
                logging.error('Select account - Invalid input please try again')