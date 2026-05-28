import pandera.pandas as pa

input_schema_validator = pa.DataFrameSchema(
    {
        'Date': pa.Column(pa.DateTime),
        'Amount': pa.Column(int),
        'Desc': pa.Column(str, pa.Check.str_length(min_value=1)),
        'Balance': pa.Column(int)
    },
    strict=True,
    coerce=False,
)

master_record_validator = pa.DataFrameSchema(
    {
        'Date': pa.Column(pa.DateTime),
        'Amount': pa.Column(int),
        'Desc': pa.Column(str, pa.Check.str_length(min_value=1)),
        'Balance': pa.Column(int),
        'Account Name': pa.Column(str),
        'Account Type': pa.Column(str)
    }
)

accounts_validator = pa.DataFrameSchema(
    {
        'Account Name': pa.Column(str),
        'Account Type': pa.Column(str),
        'Last Updated': pa.column(pa.DateTime)
    }
)