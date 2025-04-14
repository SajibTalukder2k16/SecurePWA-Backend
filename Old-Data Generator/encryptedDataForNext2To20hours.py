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
two_hours_from_now_ms = current_time_ms + (2 * 3600 * 1000)  # 2 hours ahead
twenty_hours_from_now_ms = current_time_ms + (20 * 3600 * 1000)  # 20 hours ahead

# Distributions to use
distributions = ['uniform', 'normal', 'poisson', 'exponential', 'random', 'app_usage', 'website_usage']

# Function to generate random 16-character alphanumeric device IDs
def generate_device_id():
    return ''.join(random.choices(string.hexdigits.lower(), k=16))

# Function to assign random usage counts per device (e.g., 50, 30, random)
def get_usage_count():
    return random.choice([20, 50, random.randint(10, 100)])

# Function to generate timestamps based on different distributions (next 2-20 hours)
def generate_timestamps(distribution, num_entries):
    if distribution == 'uniform':
        hours = list(range(2, 21))
        weights = [1] * 19  # Equal probability for all hours
    elif distribution == 'normal':
        hours = list(range(2, 21))
        weights = [3 if 6 <= h <= 10 else 1 for h in hours]  # Peak around 6-10 hours from now
    elif distribution == 'poisson':
        hours = list(range(2, 21))
        weights = [3 if 12 <= h <= 16 else 1 for h in hours]  # Peak around 12-16 hours from now
    elif distribution == 'exponential':
        hours = list(range(2, 21))
        weights = [3 if 18 <= h <= 20 else 1 for h in hours]  # More activity in the last 2 hours
    elif distribution == 'random':
        hours = list(range(2, 21))
        weights = np.random.rand(19)  # Fully random weight for each hour
    elif distribution == 'app_usage':
        hours = list(range(2, 21))
        weights = [4 if (6 <= h <= 9 or 17 <= h <= 19) else 1 for h in hours]  # App peaks: Morning & evening
    elif distribution == 'website_usage':
        hours = list(range(2, 21))
        weights = [4 if (10 <= h <= 12 or 14 <= h <= 16) else 1 for h in hours]  # Website peaks: Mid-morning & afternoon
    else:
        raise ValueError("Unknown distribution")

    # Normalize weights
    weights = np.array(weights) / sum(weights)

    chosen_hours = np.random.choice(hours, size=num_entries, p=weights)

    timestamps_ms = []
    for h in chosen_hours:
        minutes = np.random.randint(0, 60)
        seconds = np.random.randint(0, 60)
        timestamp = two_hours_from_now_ms + ((h - 2) * 3600 * 1000) + (minutes * 60 * 1000) + (seconds * 1000)
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
    filename = f"encrypted_device_timestamps_{dist}_next_2_to_20_hours.csv"
    df.to_csv(filename, index=False)
    print(f"Encrypted dataset saved as {filename}")

    # Visualization of timestamp distribution (using raw counts)
    timestamps_converted = [datetime.fromtimestamp(ts / 1000).hour for ts in timestamps_all]

    plt.figure(figsize=(10, 6))
    plt.hist(timestamps_converted, bins=19, alpha=0.7, edgecolor='black')
    plt.title(f'Timestamp Count Distribution ({dist} distribution - Next 2-20 Hours)')
    plt.xlabel('Hour (Next 2-20 Hours)')
    plt.ylabel('Number of Timestamps')
    plt.xticks(range(2, 21))
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()