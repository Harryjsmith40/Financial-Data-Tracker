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

file_path = input("Please enter the file path of the CSV file to read and clean: ")
cleaned_data = read_and_clean(file_path)
print("Cleaned Data: \n", cleaned_data)