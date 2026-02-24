import os 
import pandas as pd
import logging

class FinancialTracker:
    """A finnacial tracker designed to help make inform make data based decisions"""    
    def __init__(self):

        # Creates a instance variable with the file path
        self.origin_path = os.getcwd()
        self.data_folder = os.path.join(self.origin_path, 'data')
        self.master_record_path = os.path.join(self.data_folder, 'master_record.csv')

        # Checking if the master file exists
        # Currently assumes ./Data/ exists if the user doesn't have ./Data/master_record.csv 
        if os.path.exists(self.master_record_path):

            # Checks structure of file is correct
            master_record = pd.read_csv(self.master_record_path)
            if master_record.columns.tolist() == ['Date', 'Amount', 'Desc', 'Balance']:
                logging.debug('master_record initialised correctly')
            else:
                raise ValueError('master_record exists with incorrect headers')
            
        # Creates it if it doesn't exist
        else:
            master_record = pd.DataFrame(columns=['Date', 'Amount', 'Desc', 'Balance'])
            if os.path.exists(self.data_folder):
                master_record.to_csv(self.master_record_path, index=False)
            else:
                os.mkdir(self.data_folder)
                master_record.to_csv(self.master_record_path, index=False)


    def read_and_clean(self, file_path):
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path, names=['Date', 'Amount', 'Desc', 'Balance'], header=None, parse_dates=['Date'], dayfirst=True)

        # Sort by date to maintain chronological order
        df.sort_values(by=['Date'], inplace=True, ascending=True)

        # Drops na values if the amount or date is missing
        df.dropna(subset=['Date','Amount'], inplace=True)

        # Add index as transaction ID
        df.insert(0, 'Transaction ID', range(1, len(df) + 1))
        df.set_index('Transaction ID', inplace=True)

        self.to_master(df)

        return df

    def to_master(self, df):
        """Updates master_record.csv to include new data"""
        # Appends to master_record.csv the new data
        df.to_csv(self.master_record_path, mode='a', header=False, index=False)

tracker = FinancialTracker()
file_path = 'Personal.csv' # input("Please enter the file path of the CSV file to read and clean: ")
tracker.read_and_clean(file_path)