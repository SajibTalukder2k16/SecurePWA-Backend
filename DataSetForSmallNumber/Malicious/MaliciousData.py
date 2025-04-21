#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 15:42:36 2025

@author: sajib
"""


import pandas as pd
import random
import string
import time
import datetime
import matplotlib.pyplot as plt
from Crypto.Cipher import AES
import binascii
import os

# Parameters
num_devices = 20
num_unique_devices = 20
min_requests = 25
max_requests = 45


# Create dynamic paths
base_dir = f"Input/User_{num_devices}/Attack_Device_{num_unique_devices}"
csv_filename = os.path.join(base_dir, f"{num_devices}_{num_unique_devices}.csv")
total_plot_path = os.path.join(base_dir, "total_requests.png")
device_plot_path = os.path.join(base_dir, "device_distribution_plot.png")
os.makedirs(base_dir, exist_ok=True)

# AES encryption class
class MCrypt:
    def __init__(self, secret_key, iv):
        self.secret_key = secret_key.encode('utf-8')
        self.iv = iv.encode('utf-8')

    def pad(self, s):
        pad_length = 16 - (len(s) % 16)
        return s + chr(pad_length) * pad_length

    def unpad(self, s):
        return s[:-ord(s[-1])]

    def encrypt(self, raw_data):
        cipher = AES.new(self.secret_key, AES.MODE_CBC, self.iv)
        raw_data = self.pad(raw_data).encode('utf-8')
        encrypted = cipher.encrypt(raw_data)
        return binascii.hexlify(encrypted).decode('utf-8')

    def decrypt(self, encrypted_data):
        cipher = AES.new(self.secret_key, AES.MODE_CBC, self.iv)
        decrypted = cipher.decrypt(binascii.unhexlify(encrypted_data))
        return self.unpad(decrypted.decode('utf-8'))

# Generate random device ID
def generate_device_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# Define encryption keys
SECRET_KEY = "lhoiyrtevcyrtfvs"
IV = "usrqutsvbxcjpoyt"
mcrypt = MCrypt(SECRET_KEY, IV)

# App-like usage distribution over 24 hours (normalized to sum to 1)
hourly_usage_distribution = [
    0.01, 0.005, 0.003, 0.002, 0.003, 0.01,   # 12AM - 5AM
    0.03, 0.05, 0.08, 0.10, 0.10, 0.08,       # 6AM - 11AM
    0.07, 0.09, 0.09, 0.08, 0.07, 0.06,       # 12PM - 5PM
    0.05, 0.035, 0.02, 0.01, 0.007, 0.004     # 6PM - 11PM
]
hourly_usage_distribution = [x / sum(hourly_usage_distribution) for x in hourly_usage_distribution]

def generate_data(num_devices, num_unique_devices, min_requests, max_requests):
    data_list = []
    current_time = datetime.datetime.now()

    unique_device_ids = [generate_device_id() for _ in range(num_unique_devices)]

    for user_id in range(1, num_devices + 1):
        num_requests = random.randint(min_requests, max_requests)
        start_device_index = random.randint(0, num_unique_devices - 1)

        for i in range(num_requests):
            # Pick hour based on usage pattern
            hour = random.choices(range(24), weights=hourly_usage_distribution, k=1)[0]
            hour_start = current_time.replace(hour=hour, minute=0, second=0, microsecond=0)
            timestamp = hour_start + datetime.timedelta(seconds=random.randint(0, 3599))

            # Round-robin device assignment
            device_index = (start_device_index + i) % num_unique_devices
            device_id = unique_device_ids[device_index]

            raw_data = f"{int(timestamp.timestamp() * 1000)}@PWA{device_id}"
            encrypted_param = mcrypt.encrypt(raw_data)
            assert mcrypt.decrypt(encrypted_param) == raw_data

            data_list.append([user_id, device_id, int(timestamp.timestamp() * 1000), hour, raw_data, encrypted_param])

    df = pd.DataFrame(data_list, columns=["user_id", "deviceId", "timestamp", "hour", "rawData", "encryptedParam"])
    return df

def plot_data(df, total_plot_path="total_plot.png", device_plot_path="device_plot.png"):
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['hour'] = df['timestamp'].dt.hour

    # Plot total requests per hour
    request_counts = df.groupby('hour').size()
    plt.figure(figsize=(10, 5))
    plt.plot(request_counts.index, request_counts.values, marker='o', linestyle='-', color='b', label="Total")
    plt.xlabel("Hour")
    plt.ylabel("Number of Requests")
    plt.title("Total Request Distribution Over 24 Hours")
    plt.xticks(range(0, 24))
    plt.grid()
    plt.legend()
    plt.savefig(total_plot_path)
    plt.show()

    # Plot requests per hour per device with different markers
    plt.figure(figsize=(12, 6))
    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x', 'X', 'd']
    devices = df['deviceId'].unique()

    for i, device_id in enumerate(devices):
        device_df = df[df['deviceId'] == device_id]
        hourly_counts = device_df.groupby('hour').size()
        marker = markers[i % len(markers)]
        plt.plot(hourly_counts.index, hourly_counts.values, marker=marker, linestyle='-', label=str(device_id))

    plt.xlabel("Hour")
    plt.ylabel("Number of Requests")
    plt.title("Request Distribution per Device Over 24 Hours")
    plt.xticks(range(0, 24))
    plt.grid()
    plt.tight_layout()
    plt.legend(fontsize='small', loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.savefig(device_plot_path)
    plt.show()

if __name__ == "__main__":
    df = generate_data(num_devices, num_unique_devices, min_requests, max_requests)

    # Summary Report
    total_requests = len(df)
    successful_requests = total_requests
    unique_device_count = df['deviceId'].nunique()
    total_device_entries = len(df['deviceId'])
    copied_devices = total_device_entries - unique_device_count
    avg_requests_per_device = total_requests / unique_device_count if unique_device_count else 0
    avg_requests_per_user = total_requests / num_devices if num_devices else 0

    print("\n--- Summary Report ---")
    print(f"Total requests: {total_requests}")
    print(f"Number of Users: {num_devices}")
    print(f"Number of Attack devices: {unique_device_count}")
    print(f"Total Users: {total_device_entries}")
    print(f"Copied (duplicated) devices: {copied_devices}")
    print(f"Average requests per device: {avg_requests_per_device:.2f}")
    print(f"Average requests per user: {avg_requests_per_user:.2f}")
    df = df.sample(frac=1).reset_index(drop=True)
    df.to_csv(csv_filename, index=False)
    print(f"Data saved to {csv_filename}")
    plot_data(df)
