import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mplsoccer import Pitch
import ast
import re


data_path = "../../../data/small/"


def possession_team_catcher(text):
    possession_team_pattern = r"Possession:\s*([\w]+(?:\s[\w]+)*)"

    match = re.search(possession_team_pattern, text)
    if match:
        possession_team = match.group(1)
    else:
        possession_team = None
    
    return possession_team

event_df = pd.read_csv(data_path + '15956.csv')
event_df['start_loc'] = event_df['start_loc'].apply(ast.literal_eval)
event_df['end_loc'] = event_df['end_loc'].apply(ast.literal_eval)

# Initialize the pitch
fig, ax = plt.subplots(figsize=(15, 9))
pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white',pitch_length=120, pitch_width=80)
pitch.draw(ax=ax)

# Elements to update during animation
ball_marker, = ax.plot([], [], 'wo', markersize=15, markeredgewidth=1, markeredgecolor='black')  
ball_text = ax.text(0, 0, '', ha='center', va='center', fontsize=7, color='black', fontweight='bold')  

popup_text = ax.text(50, 85, '', ha='center', va='center', fontsize=12, color='white', 
                      bbox=dict(facecolor='black', edgecolor='white', boxstyle='round,pad=0.5'))

arrow = ax.annotate("", xy=(0, 0), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color="white", lw=2))

color_mapping = {'TeamA': 'c', 'TeamB': 'm'}

def update(frame):
    frame += 1 # skip the first event which is the half start
    event = event_df.iloc[frame]
    x,y = event['start_loc'][0], event['start_loc'][1]
    x_end,y_end = event['end_loc'][0], event['end_loc'][1]
    player_pos = event['player_pos']
    text = event['text']
    outcome = event['outcome']
    team_color = color_mapping[possession_team_catcher(text)]

    ball_marker.set_data([x], [y])
    ball_marker.set_color(team_color)

    ball_text.set_position((x, y))
    ball_text.set_text(player_pos)

    if x_end is not None: # event has a destination
        arrow.set_position((x, y))
        arrow.xy = (x_end, y_end)
    else:
        arrow.set_position((0, 0))
        arrow.xy = (0, 0)

    # Show incomplete action
    if outcome == 'Incomplete':
        arrow.arrow_patch.set_color('red')
    else:
        arrow.arrow_patch.set_color('white')
        

    popup_text.set_text(text)
    popup_text.set_position((x, y - 6))  # Move popup slightly above the ball

    return ball_marker, ball_text, popup_text, arrow


if __name__ == "__main__":
    # Animate with 2s delay between frames
    frames = len(event_df)-1
    ani = FuncAnimation(fig, update, frames=10, interval=2000, repeat=True)
    plt.show()
    ani.save("match_animation.gif", writer='pillow')
