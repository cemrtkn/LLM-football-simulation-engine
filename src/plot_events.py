import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mplsoccer import Pitch
import json

data_path = "../data/small_sample.json"
data = None

with open(data_path, "r") as file:
    data = json.load(file)

# Initialize the pitch
fig, ax = plt.subplots(figsize=(10, 6))
pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white',pitch_length=120, pitch_width=80)
pitch.draw(ax=ax)

# Elements to update during animation
ball_marker, = ax.plot([], [], 'wo', markersize=15, markeredgewidth=1, markeredgecolor='black')  
ball_text = ax.text(0, 0, '', ha='center', va='center', fontsize=8, color='black', fontweight='bold')  

popup_text = ax.text(50, 85, '', ha='center', va='center', fontsize=12, color='white', 
                      bbox=dict(facecolor='black', edgecolor='white', boxstyle='round,pad=0.5'))

def team_to_color(events):
    teams = []
    for event in events:
        team_id = str(event['team']['id'])
        if team_id not in teams:
            teams.append(team_id)
        if len(team_id) == 2:
            break
    mapping = {teams[0]: 'c', teams[1]: 'm'}
    return mapping
def coordinate_inverter(mapping, team_id, x, y):
    # event coordinates come for both teams relative to their goal
    teams = list(mapping.keys())
    if team_id == teams[1]:
        x = 120-x
        y = 80-y
    return x,y

color_mapping = team_to_color(data)

def update(frame):
    event = data[frame]
    x, y = event['location']
    team_id = str(event['team']['id'])
    x, y = coordinate_inverter(color_mapping, team_id, x, y)
    possession_idx = event['possession']

    player_pos = "".join(word[0] for word in event['position']['name'].split())

    # Fix: Wrap x and y in lists
    ball_marker.set_data([x], [y])
    ball_marker.set_color(color_mapping[team_id])
    ball_text.set_position((x, y))
    ball_text.set_text(player_pos)

    event_type = event['type']['name']
    if event_type == "Goal Keeper":
        text = f"{possession_idx}. Time: {event['timestamp']} | Phase: {event['play_pattern']['name']} | Event: {event_type} | Type: {event['goalkeeper']['type']['name']}"

    elif event_type == "Duel":
        if event['duel']['type']['name'] == "Tackle":
            outcome = event['duel']['outcome']
            text = f"{possession_idx}. Time: {event['timestamp']} | Phase: {event['play_pattern']['name']} | Event: {event_type} | Type: {event['duel']['type']['name']} | Outcome: {outcome}"

        elif event['duel']['type']['name'] == "Aerial Lost":
            text = f"{possession_idx}. Time: {event['timestamp']} | Phase: {event['play_pattern']['name']} | Event: {event_type} | Type: {event['duel']['type']['name']}"
    
    elif event_type == "Ball Receipt*" and event.get("ball_receipt") is not None:
        outcome = event['ball_receipt']['outcome']['name']
        text = f"{possession_idx}. Time: {event['timestamp']} | Phase: {event['play_pattern']['name']} | Event: {event_type} | Outcome: {outcome}"

    elif event_type == "Pass" and event['pass'].get("outcome") is not None:
        outcome = event['pass']['outcome']['name']
        text = f"{possession_idx}. Time: {event['timestamp']} | Phase: {event['play_pattern']['name']} | Event: {event_type} | Outcome: {outcome}"

    else:
        text = f"{possession_idx}. Time: {event['timestamp']} | Phase: {event['play_pattern']['name']} | Event: {event_type}"
    
    popup_text.set_text(text)
    popup_text.set_position((x, y - 6))  # Move popup slightly above the ball

    
    return ball_marker, popup_text

# Animate with 2s delay between frames
ani = FuncAnimation(fig, update, frames=len(data), interval=2000, repeat=True)

plt.show()
