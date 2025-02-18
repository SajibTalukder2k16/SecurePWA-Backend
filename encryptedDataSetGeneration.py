import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time
import random
import string
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import binascii  # For hex encoding & decoding

# Encryption Keys
SECRET_KEY = b'lhoiyrtevcyrtfvs'  # 16 bytes key
IV = b'usrqutsvbxcjpoyt'  # 16 bytes IV

# Function to encrypt data using AES-CBC (Hexadecimal Output)
def encrypt_data(plain_text):
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)
    padded_text = pad(plain_text.encode(), AES.block_size)  # Padding
    encrypted_bytes = cipher.encrypt(padded_text)
    return binascii.hexlify(encrypted_bytes).decode()  # Convert to HEX

# Get the current time in milliseconds
current_time_ms = int(time.time() * 1000)
one_hour_ago_ms = current_time_ms - (1 * 3600 * 1000)  # 1 hour back

# Distributions to use
distributions = ['uniform', 'normal', 'poisson', 'exponential', 'random', 'app_usage', 'website_usage']

# Function to generate random 16-character alphanumeric device IDs
def generate_device_id():
    return ''.join(random.choices(string.hexdigits.lower(), k=16))

# Function to assign random usage counts per device (e.g., 50, 30, random)
def get_usage_count():
    return random.choice([20, 50, random.randint(10, 100)])

# Function to generate timestamps based on different distributions (last 1 hour)
def generate_timestamps(distribution, num_entries):
    if distribution == 'uniform':
        minutes = list(range(0, 60))
        weights = [1] * 60  # Equal probability for all minutes
    elif distribution == 'normal':
        minutes = list(range(0, 60))
        weights = [3 if 10 <= m <= 30 else 1 for m in minutes]  # Peak around 10-30 minutes ago
    elif distribution == 'poisson':
        minutes = list(range(0, 60))
        weights = [3 if 30 <= m <= 50 else 1 for m in minutes]  # Peak around 30-50 minutes ago
    elif distribution == 'exponential':
        minutes = list(range(0, 60))
        weights = [3 if 40 <= m <= 59 else 1 for m in minutes]  # More activity in the last 20 minutes
    elif distribution == 'random':
        minutes = list(range(0, 60))
        weights = np.random.rand(60)  # Fully random weight for each minute
    elif distribution == 'app_usage':
        minutes = list(range(0, 60))
        weights = [4 if (5 <= m <= 15 or 45 <= m <= 55) else 1 for m in minutes]  # Peak at 5-15 min & 45-55 min
    elif distribution == 'website_usage':
        minutes = list(range(0, 60))
        weights = [4 if (20 <= m <= 30 or 50 <= m <= 59) else 1 for m in minutes]  # Peak at 20-30 min & 50-59 min
    else:
        raise ValueError("Unknown distribution")

    # Normalize weights
    weights = np.array(weights) / sum(weights)

    chosen_minutes = np.random.choice(minutes, size=num_entries, p=weights)

    timestamps_ms = []
    for m in chosen_minutes:
        seconds = np.random.randint(0, 60)
        timestamp = one_hour_ago_ms + (m * 60 * 1000) + (seconds * 1000)
        timestamps_ms.append(int(timestamp))

    timestamps_ms.sort()
    return timestamps_ms
num_devices = 30
# Generate datasets and encrypt
for dist in distributions:
    dataset = []
    timestamps_all = []
    for _ in range(num_devices):
        device_id = generate_device_id()
        usage_count = get_usage_count()
        timestamps = generate_timestamps(dist, usage_count)

        timestamps_all.extend(timestamps)

        for ts in timestamps:
            encrypted_deviceID = encrypt_data(device_id)
            encrypted_timestamp = encrypt_data(str(ts))  # Convert timestamp to string before encrypting
            dataset.append({"deviceID": encrypted_deviceID, "timestamp": encrypted_timestamp})

    # Convert to DataFrame
    df = pd.DataFrame(dataset)

    # Save to CSV
    filename = f"encrypted_device_timestamps_{dist}_last_1_hour.csv"
    df.to_csv(filename, index=False)
    print(f"Encrypted dataset saved as {filename}")

    # Visualization of timestamp distribution (using raw counts)
    timestamps_converted = [datetime.fromtimestamp(ts / 1000).minute for ts in timestamps_all]

    plt.figure(figsize=(10, 6))
    plt.hist(timestamps_converted, bins=30, alpha=0.7, edgecolor='black')
    plt.title(f'Timestamp Count Distribution ({dist} distribution - Last 1 Hour)')
    plt.xlabel('Minute (Last 60 Minutes)')
    plt.ylabel('Number of Timestamps')
    plt.xticks(range(0, 60, 5))
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()