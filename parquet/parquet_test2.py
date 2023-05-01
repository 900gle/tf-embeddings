import pandas as pd

df = pd.read_parquet('products.parquet', engine='pyarrow')
df.to_parquet('products3.parquet', engine='pyarrow', index=False)
