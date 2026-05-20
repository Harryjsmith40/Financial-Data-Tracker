import pandera.pandas as pa

input_schema_validator = pa.DataFrameSchema(
    {
        "Date": pa.Column(pa.DateTime),
        "Amount": pa.Column(float),
        "Desc": pa.Column(str, pa.Check.str_length(min_value=1)),
        "Balance": pa.Column(float)
    },
    strict=True,
    coerce=False,
)