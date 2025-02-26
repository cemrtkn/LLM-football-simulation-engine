
import pandas as pd
import os


sample_path = '../../data/small/'
file_name = '7298.csv'

def process(match_file, path_to_match, context_length=10):
        match_id = match_file.split(".")[0]
        match_df = pd.read_csv(os.path.join(path_to_match, match_file))

        ft_data = {"match_id": [], "input": [], "output": []}

        for id, row in match_df.iterrows():
            if id > 0:
                context_start = max(0, id - context_length)
                if id < 9:
                    context = "[match_start]\n" + "\n".join(match_df.iloc[context_start:id]['text'])
                else:
                    context = "\n".join(match_df.iloc[context_start:id]['text'])
            else:
                context = "[match_start]"


            ft_data["match_id"].append(match_id)
            ft_data["input"].append(context)
            ft_data["output"].append(row['text'])

        return ft_data

ft_data = pd.DataFrame(process(file_name, sample_path))

print(ft_data['output'][3])