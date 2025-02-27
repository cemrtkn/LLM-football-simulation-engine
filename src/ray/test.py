
import pandas as pd
import os


sample_path = '../../data/small/'
file_name = '15946.csv'

def process(match_file, path_to_match, context_length=10):
        system_prompt = "This is a sequence of football match events.\n"
        match_id = match_file.split(".")[0]
        match_df = pd.read_csv(os.path.join(path_to_match, match_file))

        ft_data = {"match_id": [], "text": []}

        for id, row in match_df.iterrows():
            if id > 0:
                context_start = max(0, id - context_length)
                if id < 9:
                    context = "[match_start]\n" + "\n".join(match_df.iloc[context_start:id]['text'])                     
                else:
                    context = "\n".join(match_df.iloc[context_start:id]['text'])
            else:
                context = "[match_start]"


            text = f"{system_prompt}{context}\n{row['text']}"
            if id == len(match_df)-1:
                 text += "\n[match_end]"
            ft_data["match_id"].append(match_id)
            ft_data["text"].append(text)

        return ft_data

ft_data = pd.DataFrame(process(file_name, sample_path))

print(ft_data['text'][0])
print(ft_data['text'][3163])