import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mplsoccer import Pitch

# Sample event data: replace this with your real dataset
data = pd.DataFrame({
    'index': [0, 1, 2, 3, 4],
    'coordinates': [(40, 30), (50, 40), (60, 20), (55, 55), (70, 35)],
    'timestamp': ['00:10', '00:15', '00:22', '00:30', '00:40'],
    'type': ['Pass', 'Shot', 'Tackle', 'Foul', 'Goal'],
    'player_pos': ['GK', 'RB', 'CB', 'LB', 'CM']
})

# Initialize the pitch
fig, ax = plt.subplots(figsize=(10, 6))
pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
pitch.draw(ax=ax)

# Elements to update during animation
ball_marker, = ax.plot([], [], 'wo', markersize=15, markeredgewidth=1, markeredgecolor='black')  
ball_text = ax.text(0, 0, '', ha='center', va='center', fontsize=8, color='black', fontweight='bold')  

popup_text = ax.text(50, 85, '', ha='center', va='center', fontsize=12, color='white', 
                      bbox=dict(facecolor='black', edgecolor='white', boxstyle='round,pad=0.5'))

# Update function for animation
def update(frame):
    event = data.iloc[frame]
    x, y = event['coordinates']
    player_pos = event['player_pos']
    
    # Fix: Wrap x and y in lists
    ball_marker.set_data([x], [y])
    ball_text.set_position((x, y))
    ball_text.set_text(player_pos)
    
    # Update popup text
    popup_text.set_text(f"Time: {event['timestamp']} | Event: {event['type']}")
    popup_text.set_position((x, y - 6))  # Move popup slightly above the ball

    
    return ball_marker, popup_text

# Animate with 2s delay between frames
ani = FuncAnimation(fig, update, frames=len(data), interval=2000, repeat=True)

plt.show()
