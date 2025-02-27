
import pandas as pd
import os


sample_path = '../../data/small/'
file_name = '15946.csv'

def process(match_file, path_to_match, context_length=10):
        system_prompt = "This is a sequence of football match events."
        match_id = match_file.split(".")[0]
        match_df = pd.read_csv(os.path.join(path_to_match, match_file))

        ft_data = {"match_id": [], "text": []}

        for id, row in match_df.iterrows():
            context_start = max(0, id - context_length)
            context = "\n" + "\n".join(match_df.iloc[context_start:id]['text'])   

            if id > 0:                  
                text = f"{system_prompt}{context}\n{row['text']}"
            else:
                text = f"{system_prompt}\n{row['text']}"
            
            ft_data["match_id"].append(match_id)
            ft_data["text"].append(text)

        return ft_data

ft_data = pd.DataFrame(process(file_name, sample_path))

print('-'*40)
print(ft_data['text'][0])
print('-'*40)
print(ft_data['text'][len(ft_data)-1])