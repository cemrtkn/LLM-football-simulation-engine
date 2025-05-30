import json
import os
import pandas as pd
import numpy as np
import re

def team_to_generic(events):
    teams = []
    for event in events:
        team_id = str(event['team']['id'])
        if team_id not in teams:
            teams.append(team_id)
        if len(teams) == 2:
            break
    mapping = {teams[0]: 'TeamA', teams[1]: 'TeamB'}
    return mapping
def coordinate_inverter(mapping, team_id, x, y):
    # event coordinates come for both teams relative to their goal
    teams = list(mapping.keys())
    if team_id == teams[1]:
        x = 120-x
        y = 80-y
    x = float(np.round(x, decimals=2))
    y = float(np.round(y, decimals=2))
    return x,y

def outcome_catcher(text):
    outcome_pattern = r"Outcome:\s*([\w\s]+)"

    match = re.search(outcome_pattern, text)
    if match:
        outcome = match.group(1)
    else:
        outcome = None
    
    return outcome


matches_dir = '../data/big/'
save_path = "../data/small/"

allowed_events = ['Shot', 'Pass', 'Ball Receipt*', 'Ball Recovery',
                  'Miscontrol', 'Dispossessed', 'Interception', 'Duel',
                  'Clearance', 'Dribble', 'Carry', 'Goal Keeper',
                  'Foul Committed', "Half End", "Half Start"]

for match_file in os.listdir(matches_dir):
    print(match_file)
    small_events = {'match_id': [], 'event_id': [], 'team_name': [],
                    'possession_id': [], 'player_pos': [] ,'start_loc': [],
                    'end_loc': [] ,'text': [], 'outcome': []}

    match_id = match_file.split('.')[0]
    with open(matches_dir + match_file , "r") as file:
        data = json.load(file)
    generic_name_mapping = team_to_generic(data)

    print(len(data))
    for event in data:
        event_type = event['type']['name']
        if event_type in allowed_events:
            team_id = str(event['team']['id'])
            text = None
            outcome = None
            x,y = None, None
            x_end,y_end = None, None
            team_generic_name = generic_name_mapping[team_id]
            possession_idx = event.get('possession')
            player_pos = None

            if event_type in ["Half End", "Half Start"]: 
                if team_id == list(generic_name_mapping.keys())[0]:# take only one of the 2 events for half end(s) start(s)
                    text = f"Time: {event['timestamp']} | Event: {event_type}"
                else:
                    continue # skip the duplicate

            else:
                pos_dict = event.get('position')
                player_pos = "".join(word[0] for word in pos_dict.get('name').split()) 

                if event_type == "Goal Keeper":
                    text = f"Time: {event['timestamp']} | Possession: {team_generic_name} | Phase: {event['play_pattern']['name']} | Player Position: {player_pos} | Event: {event_type} | Type: {event['goalkeeper']['type']['name']}"

                elif event_type == "Duel":
                    if event['duel']['type']['name'] == "Aerial Lost":
                        text = f"Time: {event['timestamp']} | Possession: {team_generic_name} | Phase: {event['play_pattern']['name']} | Player Position: {player_pos} | Event: {event_type} | Type: {event['duel']['type']['name']}"
                    
                    elif event['duel']['type']['name'] == "Tackle":
                        outcome = event['duel']['outcome']['name'] # special for tackle
                        text = f"Time: {event['timestamp']} | Possession: {team_generic_name} | Phase: {event['play_pattern']['name']} | Player Position: {player_pos} | Event: {event_type} | Type: {event['duel']['type']['name']} | Outcome: {outcome}"
            
                elif event_type == "Ball Receipt*" and event.get("ball_receipt") is not None:
                    outcome = event['ball_receipt']['outcome']['name']
                    text = f"Time: {event['timestamp']} | Possession: {team_generic_name} | Phase: {event['play_pattern']['name']} | Player Position: {player_pos} | Event: {event_type} | Outcome: {outcome}"
                
                elif event_type == "Shot" and event.get("shot") is not None:
                    outcome = event['shot']['outcome']['name']
                    text = f"Time: {event['timestamp']} | Possession: {team_generic_name} | Phase: {event['play_pattern']['name']} | Player Position: {player_pos} | Event: {event_type} | Outcome: {outcome}"

                elif event_type == "Pass" and event['pass'].get("outcome") is not None:
                    outcome = event['pass']['outcome']['name']
                    text = f"Time: {event['timestamp']} | Possession: {team_generic_name} | Phase: {event['play_pattern']['name']} | Player Position: {player_pos} | Event: {event_type} | Outcome: {outcome}"

                elif event_type == "Interception" and event['interception'].get("outcome") is not None:
                    outcome = event['interception']['outcome']['name']
                    text = f"Time: {event['timestamp']} | Possession: {team_generic_name} | Phase: {event['play_pattern']['name']} | Player Position: {player_pos} | Event: {event_type} | Outcome: {outcome}"
                
                elif event_type == "Dribble" and event['dribble'].get("outcome") is not None:
                    outcome = event['dribble']['outcome']['name']
                    text = f"Time: {event['timestamp']} | Possession: {team_generic_name} | Phase: {event['play_pattern']['name']} | Player Position: {player_pos} | Event: {event_type} | Outcome: {outcome}"
                else:
                    text = f"Time: {event['timestamp']} | Possession: {team_generic_name} | Phase: {event['play_pattern']['name']} | Player Position: {player_pos} | Event: {event_type}"
                

                # Add position info
                if event.get('location'):
                    x, y = event['location']
                elif(event.get('location') is None) and (event_type == 'Goal Keeper'): # add location to saves
                    if team_generic_name == 'TeamA':
                        x = 0
                        y = 40
                    elif team_generic_name == 'TeamB':
                        x = 120
                        y = 40

                x, y = coordinate_inverter(generic_name_mapping, team_id, x, y)
                sub_key = "_".join(event_type.lower().split())

                if (event.get(sub_key) is not None) and (event[sub_key].get('end_location') is not None):

                    end_coord_list = list(event["_".join(event_type.lower().split())].get('end_location'))
                    x_end = end_coord_list[0]
                    y_end = end_coord_list[1]

                    x_end, y_end = coordinate_inverter(generic_name_mapping, team_id, x_end, y_end)

                    text = f"Start position: ({x}, {y}), End Position: ({x_end}, {y_end}) | " + text


                elif text != None:
                    text = f"Start position: ({x}, {y}) | " + text


            small_events['match_id'].append(match_id)
            small_events['event_id'].append(len(small_events['event_id']))
            small_events['team_name'].append(team_generic_name)
            small_events['possession_id'].append(possession_idx)
            small_events['player_pos'].append(player_pos)
            small_events['start_loc'].append((x,y))
            small_events['end_loc'].append((x_end,y_end))
            small_events['text'].append(text)
            small_events['outcome'].append(outcome_catcher(text))

    small_events_df = pd.DataFrame(small_events)
    small_events_df.to_csv(save_path + match_id + '.csv')