import pandas as pd
from tqdm import tqdm
import os

path_to_match = '../data/small/'
path_to_save = '../data/ft_data/data.pkl'

def add_context(df, id, context_length):
    context = "[match_start]"
    if id == 0:
        return context
    elif id <= context_length:
        context_length = id

    for id_prev in range(id-context_length, id):
        context += "\n" + df.iloc[id_prev]['text']
    return context

counter = 0
ft_data = {'match_id': [], 'text':[]}
context_length = 10
counter = 0
for match_file in tqdm(os.listdir(path_to_match)):
    match_id = match_file.split('.')[0]
    with open(path_to_match + match_file , "r") as file:
        match_df = pd.read_csv(file)

    for id, row in match_df.iterrows():
        context = add_context(match_df, id, context_length)
        text = context + "\n" + row['text']

        ft_data['text'].append(text)
        ft_data['match_id'].append(match_id)
    
    if counter == 10:
        break

    counter += 1

ft_data = pd.DataFrame(ft_data)
ft_data.to_parquet(path_to_save.replace('.pkl', '.parquet'), engine='pyarrow', compression='snappy')
