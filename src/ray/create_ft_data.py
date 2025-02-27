import pandas as pd
import os
import ray
from ray.util.actor_pool import ActorPool

ray.init(ignore_reinit_error=True)

path_to_match = "/mnt/ceph/storage/data-tmp/current/kavo1286/personal/data/small/"
path_to_save = "/mnt/ceph/storage/data-tmp/current/kavo1286/personal/data/ft_data/"

@ray.remote
class FileProcessor:
    def process(self, match_file, path_to_match, context_length=10):
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

workers = [FileProcessor.remote() for _ in range(5)]
pool = ActorPool(workers)

match_files = os.listdir(path_to_match)
nums = [1000,2000,3000,len(match_files)]
num_prev = 0
for num in nums:
    file_batch = match_files[num_prev:num]

    results = list(pool.map(lambda a, f: a.process.remote(f, path_to_match), file_batch))

    ft_data = pd.DataFrame({k: sum([r[k] for r in results], []) for k in results[0]})
    ft_data.to_parquet(path_to_save + f'data{num}.parquet', engine="pyarrow", compression="snappy")

    num_prev = num

ray.shutdown()
