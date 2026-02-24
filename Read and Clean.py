import pandas as pd

def read_and_clean(file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path, names=['Date', 'Amount', 'Desc', 'Balance'], header=None, parse_dates=['Date'], dayfirst=True)

    # Drop rows with missing values
    df.dropna(inplace=True)

    # Sort by date to maintain chronological order
    df.sort_values(by=['Date'], inplace=True, ascending=True)

    # Add index as transaction ID after dropping rows
    df.insert(0, 'Transaction ID', range(1, len(df) + 1))
    df.set_index('Transaction ID', inplace=True)

    return df

def to_master(df):

    # Figure out how to check if master file exists and then either create one or append onto the end of one 
    df.to_csv("./Data/master_record.csv", mode='a', header=False)

    return "Complete"

file_path = input("Please enter the file path of the CSV file to read and clean: ")
cleaned_data = read_and_clean(file_path)
to_master(cleaned_data)