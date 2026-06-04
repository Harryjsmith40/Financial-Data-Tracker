class FinancialBase():
    schema = {
        'dtypes': {'Amount': float, 'Desc': str, 'Balance': float, 'Account Name': str, 'Account Type': str},
        'input_dtypes': {'Amount': float, 'Desc': str, 'Balance': float},
        'date_columns': ['Date'],
        'date_format': '%d/%m/%Y',
        'minor_date_format': '%d',
        'minor_currency_format': '${x:1.2f}',
        }