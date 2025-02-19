import json
from collections import Counter


full_file_path = "/Users/cemerturkan/Downloads/15946.json"

with open(full_file_path, "r") as file:
    data = json.load(file)


type_counts = Counter(event['type']['name'] for event in data)
counter = 0
for event_type, count in type_counts.items():
    print(f"{event_type}: {count}")
    counter += count

print('Total count:', counter)
print('Num events:', len(data))