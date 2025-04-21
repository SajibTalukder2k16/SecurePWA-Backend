#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 18 14:30:18 2025

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

# Set parameters
num_devices = 500
num_unique_devices = 20
min_requests = 25
max_requests = 45

# Create dynamic paths
base_dir = f"Malicious_User/User_{num_devices}/Attack_Device_{num_unique_devices}"
csv_filename = os.path.join(base_dir, f"{num_devices}_{num_unique_devices}.csv")
total_plot_path = os.path.join(base_dir, "total_requests.png")
device_plot_path = os.path.join(base_dir, "device_distribution_plot.png")

# Ensure directories exist
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

def generate_data(num_devices, num_unique_devices, min_requests, max_requests):
    data_list = []
    current_time = datetime.datetime.now()
    end_time = current_time + datetime.timedelta(hours=20)

    unique_device_ids = [generate_device_id() for _ in range(num_unique_devices)]

    for user_id in range(1, num_devices + 1):
        device_id = random.choice(unique_device_ids)
        num_requests = random.randint(min_requests, max_requests)

        for _ in range(num_requests):
            timestamp = current_time + datetime.timedelta(seconds=random.randint(0, 72000))
            hour = timestamp.hour

            raw_data = f"{int(timestamp.timestamp() * 1000)}@PWA{device_id}"
            encrypted_param = mcrypt.encrypt(raw_data)

            # Verify encryption correctness
            assert mcrypt.decrypt(encrypted_param) == raw_data, "Encryption/Decryption mismatch!"

            data_list.append([user_id, device_id, int(timestamp.timestamp() * 1000), hour, raw_data, encrypted_param])

    df = pd.DataFrame(data_list, columns=["user_id", "deviceId", "timestamp", "hour", "rawData", "encryptedParam"])
    return df

def plot_data(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['hour'] = df['timestamp'].dt.hour

    # Plot total requests per hour
    request_counts = df.groupby('hour').size()
    plt.figure(figsize=(10, 5))
    plt.plot(request_counts.index, request_counts.values, marker='o', linestyle='-', color='b', label="Total")
    plt.xlabel("Hour")
    plt.ylabel("Number of Requests")
    plt.title("Total Request Distribution Over 20 Hours")
    plt.xticks(range(0, 24))
    plt.grid()
    plt.legend()
    plt.savefig(total_plot_path)
    plt.show()

    # Plot requests per hour per device
    plt.figure(figsize=(12, 6))
    for device_id in df['deviceId'].unique():
        device_df = df[df['deviceId'] == device_id]
        hourly_counts = device_df.groupby('hour').size()
        plt.plot(hourly_counts.index, hourly_counts.values, marker='o', linestyle='-', label=f"{device_id}")

    plt.xlabel("Hour")
    plt.ylabel("Number of Requests")
    plt.title("Request Distribution per Device Over 20 Hours")
    plt.xticks(range(0, 24))
    #plt.legend(fontsize='small', loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.grid()
    plt.tight_layout()
    plt.savefig(device_plot_path)
    plt.show()


if __name__ == "__main__":
    #num_devices = int(input("Enter total number of Malicious User: "))
    #num_unique_devices = int(input("Enter number of attack device IDs: "))
    #min_requests = int(input("Enter minimum requests per device: "))
    #max_requests = int(input("Enter maximum requests per device: "))


    df = generate_data(num_devices, num_unique_devices, min_requests, max_requests)

    # Summary Report
    total_requests = len(df)
    successful_requests = total_requests  # All assumed successful
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
    

    #csv_filename = "Malicious_User/User_200/Attack_Device_20/200_20.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Data saved to {csv_filename}")
    plot_data(df)
