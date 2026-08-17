import os

config_path = os.path.dirname(__file__)
origin_path = os.path.dirname(config_path)
data_folder = os.path.join(origin_path, 'data')
master_record_path = os.path.join(data_folder, 'master_record.csv')
account_info_path = os.path.join(data_folder, 'accounts.csv')

schema = {
    'dtypes': {'amount': float, 'desc': str, 'balance': float, 'account_name': str, 'account_type': str},
    'input_dtypes': {'amount': float, 'desc': str, 'balance': float},
    'date_columns': ['date'],
    'date_format': '%d/%m/%Y',
    'minor_date_format': '%d',
    'minor_currency_format': '${x:1.2f}',
}