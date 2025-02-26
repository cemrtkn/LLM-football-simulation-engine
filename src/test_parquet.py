import pandas as pd
import os

# Path to your Parquet file
path_to_parquet = '../data/ft_data/'

data_files = (file for file in os.listdir(path_to_parquet) if file.endswith('parquet'))

for file in data_files:
    df = pd.read_parquet(path_to_parquet + file, engine='pyarrow')
    print(df.head())