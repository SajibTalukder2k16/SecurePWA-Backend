import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
import string

# Configuration
num_devices = 20  # Number of unique devices
date = "2025-01-24"  # Date for timestamps
peak_hours = {
    'morning': (6, 10),  # 6 AM - 10 AM
    'afternoon': (12, 16),  # 12 PM - 4 PM
    'evening': (18, 22)  # 6 PM - 10 PM
}

# Distributions to use
distributions = ['uniform', 'normal', 'poisson', 'exponential']


# Function to generate random 16-character alphanumeric device IDs
def generate_device_id():
    return ''.join(random.choices(string.hexdigits.lower(), k=16))


# Function to assign random usage counts per device (e.g., 50, 30, random)
def get_usage_count():
    return random.choice([50, 30, random.randint(20, 70)])


# Function to generate timestamps based on usage patterns
def generate_timestamps(distribution, date, usage_count):
    base_time = datetime.strptime(date, "%Y-%m-%d")
    base_timestamp_ms = int(base_time.timestamp()) * 1000  # Convert to milliseconds

    if distribution == 'uniform':
        hours = list(range(0, 24))
        weights = [1] * 24  # Equal probability for all hours
    elif distribution == 'normal':
        hours = list(range(0, 24))
        weights = [3 if 6 <= h <= 10 else 1 for h in hours]  # Higher weights for morning peak
    elif distribution == 'poisson':
        hours = list(range(0, 24))
        weights = [3 if 12 <= h <= 16 else 1 for h in hours]  # Afternoon peak
    elif distribution == 'exponential':
        hours = list(range(0, 24))
        weights = [3 if 18 <= h <= 22 else 1 for h in hours]  # Evening peak
    else:
        raise ValueError("Unknown distribution")

    chosen_hours = np.random.choice(hours, size=usage_count, p=np.array(weights) / sum(weights))

    timestamps_ms = []
    for h in chosen_hours:
        minute = np.random.randint(0, 60)
        second = np.random.randint(0, 60)
        timestamp = base_time.replace(hour=h, minute=minute, second=second)
        timestamps_ms.append(int(timestamp.timestamp()) * 1000)

    timestamps_ms.sort()
    return timestamps_ms


# Generate datasets and visualize counts
for dist in distributions:
    dataset = []
    timestamps_all = []
    for _ in range(num_devices):
        device_id = generate_device_id()
        usage_count = get_usage_count()
        timestamps = generate_timestamps(dist, date, usage_count)

        timestamps_all.extend(timestamps)

        for ts in timestamps:
            dataset.append({"deviceID": device_id, "timestamp": ts})

    # Convert to DataFrame
    df = pd.DataFrame(dataset)

    # Save to CSV
    filename = f"device_timestamps_{dist}.csv"
    df.to_csv(filename, index=False)
    print(f"Dataset saved as {filename}")

    # Visualization of timestamp distribution (using raw counts)
    timestamps_converted = [datetime.fromtimestamp(ts / 1000).hour for ts in timestamps_all]

    plt.figure(figsize=(10, 6))
    plt.hist(timestamps_converted, bins=24, alpha=0.7, edgecolor='black')
    plt.title(f'Timestamp Count Distribution ({dist} distribution)')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Number of Timestamps')
    plt.xticks(range(0, 24))
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()
