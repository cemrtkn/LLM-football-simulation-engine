import pandas as pd
import os
import ray
from ray.util.actor_pool import ActorPool

ray.init(ignore_reinit_error=True)

path_to_match = "/mnt/ceph/storage/data-tmp/current/kavo1286/personal/small/"
path_to_save = "/mnt/ceph/storage/data-tmp/current/kavo1286/personal/ft_data/data.parquet"

@ray.remote
class FileProcessor:
    def process(self, match_file, path_to_match, context_length=10):
        match_id = match_file.split(".")[0]
        match_df = pd.read_csv(os.path.join(path_to_match, match_file))

        ft_data = {"match_id": [], "text": []}

        for id, row in match_df.iterrows():
            context = "[match_start]"
            if id > 0:
                context_start = max(0, id - context_length)
                context = "[match_start]\n" + "\n".join(match_df.iloc[context_start:id]['text'])

            text = f"{context}\n{row['text']}"
            ft_data["text"].append(text)
            ft_data["match_id"].append(match_id)

        return ft_data

# Create 50 worker actors
workers = [FileProcessor.remote() for _ in range(10)]
pool = ActorPool(workers)

# Process files with limited parallelism
match_files = os.listdir(path_to_match)[:20]  # Example: Process 1000 files
results = list(pool.map(lambda a, f: a.process.remote(f, path_to_match), match_files))

# Convert results into a DataFrame
ft_data = pd.DataFrame({k: sum([r[k] for r in results], []) for k in results[0]})
ft_data.to_parquet(path_to_save, engine="pyarrow", compression="snappy")

ray.shutdown()
