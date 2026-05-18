from Config.config import schema, data_folder, master_record_path, account_info_path

import os
import pandas as pd
import logging

class FinancialTracker:
    '''A finnacial tracker designed to help make inform make data based decisions'''    
    # Defines the data types of the files and the date formatting
    schema = schema

    def __init__(self):
        '''Initialises the master record and accounts CSVs'''
        # Checking if the master file exists
        # Currently assumes ./Data/ exists if the user doesn't have ./Data/master_record.csv 
        if os.path.exists(master_record_path):
            # Checks structure of file is correct
            master_record = pd.read_csv(master_record_path)
            if master_record.columns.tolist() == ['Date', 'Amount', 'Desc', 'Balance', 'Account Name', 'Account Type']:
                logging.info('master_record initialised correctly')
            else: 
                logging.error('master_record exists with incorrect headers')
                raise ValueError('master_record exists with incorrect headers')
            
        # Creates it if it doesn't exist
        else:
            master_record = pd.DataFrame(columns=['Date', 'Amount', 'Desc', 'Balance', 'Account Name', 'Account Type'])
            if os.path.exists(data_folder):
                master_record.to_csv(master_record_path, index=False)
            else:
                os.mkdir(data_folder)
                master_record.to_csv(master_record_path, index=False)

        # Checks to see if the accounts CSV exists
        if os.path.exists(account_info_path):
            self.account_info = pd.read_csv(account_info_path)
            if self.account_info.columns.tolist() == ['Account Name', 'Account Type', 'Last Updated']:
                logging.debug('account_info initialised correctly')

        # Creates the account CSV if it doesn't
        else:
            account_info_df = pd.DataFrame(columns=['Account Name', 'Account Type', 'Last Updated'])
            account_info_df.to_csv(account_info_path, index=False)
            self.account_info = account_info_df

    def read_master(self):
        '''Reads the master file'''
        master_record = pd.read_csv(master_record_path, dtype=self.schema['dtypes'], parse_dates=self.schema['date_columns'], date_format=self.schema['date_format']
)
        return master_record

    def read_and_clean(self, file_path):
        '''Reads CSV files, formates dates and data types, removes null data and adds an index'''
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path, names=['Date', 'Amount', 'Desc', 'Balance'], header=None, dtype=self.schema['input_dtypes'], parse_dates=self.schema['date_columns'], date_format=self.schema['date_format']
)
        # Drops na values if the amount or date or balance is missing
        df.dropna(subset=['Date','Amount','Balance'], inplace=True)

        # Used to preserve intra-day transaction order from original export as resolution is 1 days but original export hold order of transactions within the day
        df.insert(0, 'Transaction Order', range(1, len(df) + 1))

        # Sort by date to maintain chronological order - Transaction Order descending as bank exports are reverse chronological
        df.sort_values(by=['Date', 'Transaction Order'], inplace=True, ascending=[True, False])
        
        # Drops column in order to preserve simplifed file
        df.drop(columns=['Transaction Order'], inplace=True)

        return df
    
    def deduplicate(self, cleaned_input):
        ''' Checks for and removes duplicates''' 
        master_record = self.read_master()
        merged_df = cleaned_input.merge(master_record, how='left', on=['Date', 'Amount', 'Desc', 'Balance', 'Account Name', 'Account Type'], indicator=True)
        merged_df = merged_df[merged_df['_merge'] == 'left_only']
        merged_df = merged_df.drop(labels='_merge' , axis='columns')

        return merged_df

    def to_master(self, df):
        '''Updates master_record.csv to include new data'''
        # Appends to master_record.csv the new data
        df.to_csv(master_record_path, mode='a', header=False, index=False, date_format=self.schema['date_format'])
    
    def create_account(self):
        '''Creates a new account'''
        account_name = input('Please provide the name of the account this data is from: ')
        account_type = input('Please provide the type of this account (e.g. current, savings, credit card): ')

        # Updates the last updated timestamp in the accounts file 
        new_account_info = pd.DataFrame({'Account Name': [account_name], 'Account Type': [account_type], 'Last Updated': [pd.Timestamp.now()]})
        new_account_info.to_csv(account_info_path, mode='a', header=False, index=False)

        return account_name, account_type

    def select_account(self):
        
        while True:
            # Iteractively prints the account names from account csvand types for the user to select from
            for index, row in self.account_info.iterrows():
                print(index, row['Account Name'])
            print('A Add New Account')
            print('B Back to main menu')

            self.account_name_option = input('Please provide the number/letter of the account this data is from: ')

            # Creates new account
            if self.account_name_option.upper() == 'A':
                account_name, account_type =  self.create_account()
                return account_name, account_type
            
            # Goes back to main menu
            elif self.account_name_option.upper() == 'B':
                break
            
            else:
                # Checks if selected option is a valid account number 
                try:
                    selection = int(self.account_name_option)
                except ValueError:
                    print('Invalid input please try again')
                    logging.info('Select account - Invalid input please try again')
                    continue

                # Checks if number falls within the range of existing accounts
                if selection < len(self.account_info):
                    # Updated the last updated timestamp on the accounts CSV
                    self.account_info.loc[selection,'Last Updated'] = str(pd.Timestamp.now())
                    self.account_info.to_csv(account_info_path, index=False)

                    # Reads the account details and returns them
                    account_name = self.account_info.loc[selection].iat[0]
                    account_type = self.account_info.loc[selection].iat[1]
                    return account_name, account_type

                # Fall back for invalid input
                else:
                    print('Invalid input please try again')

    def upload_file(self):
        '''Prompts the user for the file name'''
        
        while True:
            print('B Back to main menu')
            self.file_path_option = input('Please ensure the CSV file is in the data folder and provide the file name would like to upload: ')

            # Sends user back to main menu if selected
            if self.file_path_option.upper() == 'B':
                break
            
            # adds the rest of the file path to the file name
            self.file_path = os.path.join(data_folder, self.file_path_option)

            # Checks if the provided file/path exists
            if os.path.exists(self.file_path):
                cleaned_input = self.read_and_clean(self.file_path)
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
                self.to_master(deduplicated_input)

            # Fall back for invalid input
            else:
                logging.info('Failed file does not exist')
                raise IndexError('Upload file - Failed file does not exist')