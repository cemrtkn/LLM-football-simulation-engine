import pandas as pd
import os
import ray
from ray.util.actor_pool import ActorPool

ray.init(ignore_reinit_error=True)

path_to_match = "/mnt/ceph/storage/data-tmp/current/kavo1286/personal/small/"
path_to_save = "/mnt/ceph/storage/data-tmp/current/kavo1286/personal/ft_data/"

@ray.remote
class FileProcessor:
    def process(self, match_file, path_to_match, context_length=10):
        match_id = match_file.split(".")[0]
        match_df = pd.read_csv(os.path.join(path_to_match, match_file))

        ft_data = {"match_id": [], "text": []}

        for id, row in match_df.iterrows():
            if id > 0:
                context_start = max(0, id - context_length)
                if id < 9:
                    context = "[match_start]" + "\n".join(match_df.iloc[context_start:id]['text'])
                else:
                    context = "\n".join(match_df.iloc[context_start:id]['text'])
            else:
                context = "[match_start]"

            text = f"{context}\n{row['text']}"
            ft_data["text"].append(text)
            ft_data["match_id"].append(match_id)

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
