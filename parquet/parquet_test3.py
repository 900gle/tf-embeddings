import pyarrow as pa

import pyarrow.parquet as pq

df = pq.read_pandas('products.parquet').to_pandas()

table_from_pandas = pa.Table.from_pandas(df, preserve_index=False)
pq.write_table(table_from_pandas, 'products4.parquet')
