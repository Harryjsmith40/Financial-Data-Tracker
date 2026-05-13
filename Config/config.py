import os

config_path = os.path.dirname(__file__)
origin_path = os.path.dirname(config_path)
data_folder = os.path.join(origin_path, 'data')
master_record_path = os.path.join(data_folder, 'master_record.csv')
account_info_path = os.path.join(data_folder, 'accounts.csv')

schema = {
    'dtypes': {'Amount': float, 'Desc': str, 'Balance': float, 'Account Name': str, 'Account Type': str},
    'input_dtypes': {'Amount': float, 'Desc': str, 'Balance': float},
    'date_columns': ['Date'],
    'date_format': '%d/%m/%Y',
    'minor_date_format': '%d',
    'minor_currency_format': '${x:1.2f}',
}