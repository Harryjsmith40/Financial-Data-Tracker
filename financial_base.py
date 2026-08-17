class FinancialBase:
    def __init__(self, repo):
        self.repo = repo
        self.schema = {
        'dtypes': {'amount': float, 'desc': str, 'balance': float, 'account_name': str, 'account_type': str},
        'input_dtypes': {'amount': float, 'desc': str, 'balance': float},
        'date_columns': ['date'],
        'date_format': '%d/%m/%Y',
        'minor_date_format': '%d',
        'minor_currency_format': '${x:1.2f}',
        }