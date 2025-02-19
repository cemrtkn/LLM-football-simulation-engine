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

    player_pos = "".join(word[0] for word in event['position']['name'].split())
    event_type = event['type']['name']

    # Fix: Wrap x and y in lists
    ball_marker.set_data([x], [y])
    ball_marker.set_color(color_mapping[team_id])
    ball_text.set_position((x, y))
    ball_text.set_text(player_pos)

    popup_text.set_text(f"Time: {event['timestamp']} | Event: {event_type}")

    popup_text.set_position((x, y - 6))  # Move popup slightly above the ball

    
    return ball_marker, popup_text

# Animate with 2s delay between frames
ani = FuncAnimation(fig, update, frames=len(data), interval=2000, repeat=True)

plt.show()
