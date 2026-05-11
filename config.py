import os

origin_path = os.getcwd()
data_folder = os.path.join(origin_path, 'data')
master_record_path = os.path.join(data_folder, 'master_record.csv')
account_info_path = os.path.join(data_folder, 'accounts.csv')

schema = {
    'dtypes': {'Amount': float, 'Desc': str, 'Balance': float, 'Account Name': str, 'Account Type': str},
    'input_dtypes': {'Amount': float, 'Desc': str, 'Balance': float},
    'date_columns': ['Date'],
    'date_format': '%d/%m/%Y'
}