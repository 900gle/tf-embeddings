import pyarrow.parquet as pq
from pyarrow import csv

pq.write_table(csv.read_csv('products.csv'), 'products.parquet')


