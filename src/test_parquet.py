import pandas as pd

# Path to your Parquet file
path_to_parquet = '../data/ft_data/data.parquet'

# Load the Parquet file
df = pd.read_parquet(path_to_parquet, engine='pyarrow')

# Print the first five rows
print(len(df))
