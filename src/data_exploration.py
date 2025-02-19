import json

full_file_path = "/Users/cemerturkan/Downloads/15946.json"

with open(full_file_path, "r") as file:
    data = json.load(file)


save_path = "../data/small_sample.json"

allowed_events = ['Shot','Pass' ,'Ball Receipt*', 'Ball Recovery' ,'Miscontrol' ,'Dispossessed' ,'Interception', 'Duel', 'Clearance' ,'Dribble', 'Carry']
small_events = []

for event in data:
    if event['type']['name'] in allowed_events:
        small_events.append(event)
        
with open(save_path, "w") as file:
    json.dump(small_events, file, indent=4)