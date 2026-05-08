import os
import pandas as pd
import logging

class FinancialTracker:
    """A finnacial tracker designed to help make inform make data based decisions"""    
    # Defines the dtypes of the master record
    schema = {
        'dtypes': {'Amount': float, 'Balance': float, 'Desc': str, 'Account': str},
        'date_columns': ['Date'],
        'date_format' : '%d/%m/%Y'
        }

    def __init__(self):
        """Initialises the master record and uploads a new file"""
        # Creates a instance variable with the file path
        self.origin_path = os.getcwd()
        self.data_folder = os.path.join(self.origin_path, 'data')
        self.master_record_path = os.path.join(self.data_folder, 'master_record.csv')

        # Checking if the master file exists
        # Currently assumes ./Data/ exists if the user doesn't have ./Data/master_record.csv 
        if os.path.exists(self.master_record_path):
            # Checks structure of file is correct
            master_record = pd.read_csv(self.master_record_path)
            if master_record.columns.tolist() == ['Date', 'Amount', 'Desc', 'Balance', 'Account Name', 'Account Type']:
                logging.debug('master_record initialised correctly')
            else:
                raise ValueError('master_record exists with incorrect headers')
            
        # Creates it if it doesn't exist
        else:
            master_record = pd.DataFrame(columns=['Date', 'Amount', 'Desc', 'Balance', 'Account Name', 'Account Type'])
            if os.path.exists(self.data_folder):
                master_record.to_csv(self.master_record_path, index=False)
            else:
                os.mkdir(self.data_folder)
                master_record.to_csv(self.master_record_path, index=False)

        self.upload_file()
    
    def read_master(self):
        """Reads the master file"""
        master_record = pd.read_csv(self.master_record_path, dtype=self.schema['dtypes'], parse_dates=self.schema['date_columns'], date_format=self.schema['date_format']
)
        return master_record

    def read_and_clean(self, file_path):
        """Reads CSV files, formates dates and data types, removes null data and adds an index"""
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path, names=['Date', 'Amount', 'Desc', 'Balance'], header=None, dtype=self.schema['dtypes'], parse_dates=self.schema['date_columns'], date_format=self.schema['date_format']
)

        # Sort by date to maintain chronological order
        df.sort_values(by=['Date'], inplace=True, ascending=True)

        # Drops na values if the amount or date is missing
        df.dropna(subset=['Date','Amount'], inplace=True)

        return df
    
    def deduplicate(self, cleaned_input):
        """ Checks for and removes duplicates""" 
        master_record = self.read_master()
        merged_df = cleaned_input.merge(master_record, how='left', on=['Date', 'Amount', 'Desc', 'Balance', 'Account Name'], indicator=True)
        merged_df = merged_df[merged_df['_merge'] == 'left_only']
        merged_df = merged_df.drop(labels='_merge' , axis='columns')

        return merged_df

    def to_master(self, df):
        """Updates master_record.csv to include new data"""
        # Appends to master_record.csv the new data
        df.to_csv(self.master_record_path, mode='a', header=False, index=False, date_format=self.schema['date_format'])
    
    def upload_file(self):
        """Prompts the user to upload a file, checks if it exists and then processes it"""
        self.file_path = input("Please ensure the CSV file is in the data folder and provide the file name would like to upload: ")
        self.file_path = os.path.join(self.data_folder, self.file_path)

        self.account_name = input("Please provide the name of the account this data is from: ")
        self.account_type = input("Please provide the type of this account (e.g. current, savings, credit card): ")

        if os.path.exists(self.file_path):
            cleaned_input = self.read_and_clean(self.file_path)
            logging.debug('file_path exists correctly')

            cleaned_input['Account Name'] = self.account_name
            cleaned_input['Account Type'] = self.account_type

            deuplicated_input = self.deduplicate(cleaned_input)

            self.to_master(deuplicated_input)
        else:
            print("Failed file doesn't exist") 
            self.upload_file()

tracker = FinancialTracker()