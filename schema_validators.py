import pandera.pandas as pa

input_schema_validator = pa.DataFrameSchema(
    {
        'date': pa.Column(pa.DateTime),
        'amount': pa.Column(int),
        'desc': pa.Column(str, pa.Check.str_length(min_value=1)),
        'balance': pa.Column(int)
    },
    strict=True,
    coerce=False,
)

master_record_validator = pa.DataFrameSchema(
    {
        'date': pa.Column(pa.DateTime),
        'amount': pa.Column(int),
        'desc': pa.Column(str, pa.Check.str_length(min_value=1)),
        'balance': pa.Column(int),
        'account_name': pa.Column(str),
        'account_type': pa.Column(str)
    }
)

accounts_validator = pa.DataFrameSchema(
    {
        'account_name': pa.Column(str),
        'account_type': pa.Column(str),
        'last_updated': pa.Column(pa.DateTime)
    }
)