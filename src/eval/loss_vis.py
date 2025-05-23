import os 
import json
import matplotlib.pyplot as plt
import random

path_to_loss = "../training/outputs/outputs_Mistral-7B-sim-qlora.json"

with open(path_to_loss, "r") as f:
    data = json.load(f)

loss_values = []  # List to store loss values
steps = []       # List to store epoch numbers
lrs = []
for i, log in enumerate(data):
    loss = log.get("loss")
    step = log.get("step")
    lr = log.get("learning_rate")
    if loss is not None:
        loss_values.append(loss)
        steps.append(step)
        lrs.append(lr)


print(len(loss_values))
print(len(steps))
print(len(lrs))

def plot(x, y, title, xlabel, ylabel, filename):
    plt.figure(figsize=(10, 5))
    color = random.choice(["red", "blue", "green", "yellow", "purple", "orange", "pink", "brown", "gray", "black"])
    plt.plot(x, y, label=title, color=color)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid()
    plt.savefig(filename)  # Save the plot as a PNG file
    plt.show()  # Display the plot"""



plot(steps, loss_values, "Loss Trend Over Steps", "Steps", "Loss", "loss_trend.png")
plot(steps, lrs, "Learning Rate Trend Over Steps", "Steps", "Learning Rate", "lr_trend.png")




