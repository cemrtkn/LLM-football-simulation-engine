import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from datetime import timedelta
import pandas as pd
import numpy as np
from collections import Counter
import numpy as np
import re

def extract_event_info(text):
    pattern = (
        r"(?:Start position: \((?P<start_x>[\d\.]+), (?P<start_y>[\d\.]+)\))?"
        r"(?:, End Position: \((?P<end_x>[\d\.]+), (?P<end_y>[\d\.]+)\))?"
        r"(?:\s*\|\s*)?Time: (?P<time>\d{2}:\d{2}:\d{2}\.\d{3})"
        r"(?:\s*\|\s*Possession: (?P<team_name>[^|]+))?"
        r"(?:\s*\|\s*Phase: (?P<phase>[^|]+))?"
        r"(?:\s*\|\s*Player Position: (?P<player_pos>[^|]+))?"
        r"(?:\s*\|\s*Event: (?P<event>[^|]+))"
        r"(?:\s*\|\s*Outcome: (?P<outcome>[^|]+))?"
        r"(?:\s*\|\s*Type: (?P<type>[^|]+))?"
    )


    match = re.search(pattern, text)
    if not match:
        return None

    data = match.groupdict()

    # If event or time are missing, reject the match
    if data['event'] is None or data['time'] is None:
        return None

    # Convert coordinates to floats
    for key in ['start_x', 'start_y', 'end_x', 'end_y']:
        if data[key] is not None:
            data[key] = float(data[key])

    # Convert time to timedelta
    h, m, s = data['time'].split(':')
    sec, ms = s.split('.')
    data['time'] = timedelta(
        hours=int(h),
        minutes=int(m),
        seconds=int(sec),
        milliseconds=int(ms)
    )

    return data

def euclidean_distance(gt, pred, start):
    if start:
        p1, p2 = np.array([gt["start_x"], gt["start_y"]]), np.array([pred["start_x"], pred["start_y"]])
    else:
        p1, p2 = np.array([gt["end_x"], gt["end_y"]]), np.array([pred["end_x"], pred["end_y"]])

    # in the event that either gt or pred has no end coordinate
    counter = 0
    for p, data_type in zip([p1, p2], ["gt", "pred"]):
        if None in p:
            counter += 1
    if counter == 1:
        return None
    elif counter == 2:
        return 0

    return np.linalg.norm(p1 - p2)

def time_diff(gt, pred):
    if isinstance(gt["time"], str):
        gt["time"] = pd.to_timedelta(gt["time"])
        pred["time"] = pd.to_timedelta(pred["time"])
    return abs(gt["time"].total_seconds() - pred["time"].total_seconds())


def calculate_stats(gts, preds):
    total_time_diff = 0
    total_start_distance = 0
    total_end_distance = 0

    unmatching_end_pos = 0
    unmatching_start_pos = 0

    possession_true = 0
    phase_true = 0
    event_true = 0
    outcome_true = 0

    gt_events = []
    pred_events = []

    failed_generations = 0

    for gt, pred in zip(gts, preds):
        if pred == {}:
            failed_generations += 1
            continue
        if gt == {}:
            continue
        total_time_diff += time_diff(gt, pred)
        start_distance = euclidean_distance(gt, pred, start = True)
        end_distance = euclidean_distance(gt, pred, start = False)

        if start_distance is None:
            unmatching_start_pos += 1
        else:
            total_start_distance += start_distance

        if end_distance is None:
            unmatching_end_pos += 1
        else:
            total_end_distance += end_distance

        if gt["possession"] == pred["possession"]:
            possession_true += 1
        if gt["phase"] == pred["phase"]:
            phase_true += 1

        gt_events.append(gt["event"])
        pred_events.append(pred["event"])
        if gt["event"] == pred["event"]:
            event_true += 1
            
        if gt["outcome"] == pred["outcome"]:
            outcome_true += 1
    
    num_samples = len(gts) - failed_generations

    # --- Print scalar evaluation metrics ---
    print("\n--- Evaluation Summary ---")
    print(f"Samples evaluated: {num_samples}")
    print(f"Failed generations (syntax error): {failed_generations}")
    print(f"Avg. time difference: {total_time_diff/num_samples:.2f} seconds")
    print(f"Average start position distance: {total_start_distance / num_samples:.2f} units")
    print(f"Average end position distance: {total_end_distance / num_samples:.2f} units")
    print(f"Unmatching end positions: {unmatching_end_pos}")

    print("\n--- Label Accuracy ---")
    print(f"Possession match: {possession_true}/{num_samples} ({(possession_true / num_samples) * 100:.2f}%)")
    print(f"Phase match: {phase_true}/{num_samples} ({(phase_true / num_samples) * 100:.2f}%)")
    print(f"Event match: {event_true}/{num_samples} ({(event_true / num_samples) * 100:.2f}%)")
    print(f"Outcome match: {outcome_true}/{num_samples} ({(outcome_true / num_samples) * 100:.2f}%)")

    return {
        "total_time_diff": total_time_diff,
        "total_start_distance": total_start_distance,
        "total_end_distance": total_end_distance,
        "unmatching_end_pos": unmatching_end_pos,
        "possession_true": possession_true,
        "phase_true": phase_true,
        "event_true": event_true,
    }

def plot_confusion_matrix(gts, preds):
    all_events = ['Shot', 'Pass', 'Ball Receipt*', 'Ball Recovery',
                    'Miscontrol', 'Dispossessed', 'Interception', 'Duel',
                    'Clearance', 'Dribble', 'Carry', 'Goal Keeper',
                    'Foul Committed', "Half End", "Half Start"]

    gt_events = []
    pred_events = []

    for g, p in zip(gts, preds):
        if g.get("event") is not None and p.get("event") is not None:
            gt_events.append(g.get("event"))
            pred_events.append(p.get("event"))
        else:
            continue


    cm = confusion_matrix(gt_events, pred_events, labels=all_events)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=all_events)

    fig, ax = plt.subplots(figsize=(12, 10))
    disp.plot(ax=ax, cmap='Blues', xticks_rotation=45)
    plt.title("Confusion Matrix: Event Prediction")
    plt.tight_layout()
    plt.savefig("conf_matrix.png")
    plt.show()


def plot_bar_chart(gts, preds):
    pred_event_counter = Counter()
    gt_event_counter = Counter()
    for p, g in zip(preds, gts):
        if p.get("event") is not None:
            pred_event_counter[p["event"]] += 1 
        if g.get("event") is not None:
            gt_event_counter[g["event"]] += 1 

    # Get unique events from both predicted and ground truth
    all_events = set(pred_event_counter.keys()).union(set(gt_event_counter.keys()))

    # Prepare counts for each event
    event_counts = [(event, gt_event_counter.get(event, 0), pred_event_counter.get(event, 0)) for event in all_events]

    # Sort by ground truth counts in descending order
    event_counts.sort(key=lambda x: x[1], reverse=True)

    # Unzip the sorted events and counts
    sorted_events, gt_counts, pred_counts = zip(*event_counts)

    # Set the bar width
    bar_width = 0.35
    x = np.arange(len(sorted_events))  # The label locations

    plt.figure(figsize=(10, 5))
    plt.bar(x - bar_width/2, pred_counts, width=bar_width, label='Predicted', color='skyblue')  # Predicted bars
    plt.bar(x + bar_width/2, gt_counts, width=bar_width, label='Ground Truth', color='salmon')  # GT bars

    plt.xlabel("Event", fontsize=14)
    plt.ylabel("Count", fontsize=14)
    plt.title("Event Count Comparison", fontsize=16)
    plt.xticks(x, sorted_events, rotation=45, ha='right', fontsize=12)  # Set x-ticks to sorted events
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()  # Add a legend to differentiate between predicted and GT
    plt.tight_layout()
    plt.savefig("event_count_comparison.png")
    plt.show()
