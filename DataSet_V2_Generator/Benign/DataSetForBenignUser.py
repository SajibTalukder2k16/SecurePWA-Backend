#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 18 15:13:28 2025

@author: sajib
"""

import pandas as pd
import random
import string
import datetime
import matplotlib.pyplot as plt
from Crypto.Cipher import AES
import binascii

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

def generate_data(num_users, min_requests, max_requests):
    data_list = []
    current_time = datetime.datetime.now()
    end_time = current_time + datetime.timedelta(hours=20)

    for user_id in range(1, num_users + 1):
        device_id = generate_device_id()
        num_requests = random.randint(min_requests, max_requests)

        for _ in range(num_requests):
            timestamp = current_time + datetime.timedelta(seconds=random.randint(0, 72000))
            hour = timestamp.hour

            raw_data = f"{int(timestamp.timestamp() * 1000)}@PWA{device_id}"
            encrypted_param = mcrypt.encrypt(raw_data)

            assert mcrypt.decrypt(encrypted_param) == raw_data, "Encryption/Decryption mismatch!"

            data_list.append([user_id, device_id, int(timestamp.timestamp() * 1000), hour, raw_data, encrypted_param])

    df = pd.DataFrame(data_list, columns=["user_id", "deviceId", "timestamp", "hour", "rawData", "encryptedParam"])
    return df

def plot_data(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['hour'] = df['timestamp'].dt.hour

    request_counts = df.groupby('hour').size()
    plt.figure(figsize=(10, 5))
    plt.plot(request_counts.index, request_counts.values, marker='o', linestyle='-', color='b', label="Total")
    plt.xlabel("Hour")
    plt.ylabel("Number of Requests")
    plt.title("Total Request Distribution Over 20 Hours")
    plt.xticks(range(0, 24))
    plt.grid()
    plt.legend()
    plt.savefig("CSV/100/total_requests.png")
    plt.show()

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
    plt.savefig("CSV/100/device_distribution_plot.png")
    plt.show()

if __name__ == "__main__":
    num_users = int(input("Enter total number of Benign users: "))
    #min_requests = int(input("Enter minimum requests per device: "))
    #max_requests = int(input("Enter maximum requests per device: "))
    
    min_requests = 25
    max_requests = 45
    
    df = generate_data(num_users, min_requests, max_requests)

    total_requests = len(df)
    successful_requests = total_requests
    unique_devices = df['deviceId'].nunique()
    #copied_devices = total_requests - unique_devices
    avg_requests_per_device = total_requests / unique_devices if unique_devices else 0

    print("\n--- Summary Report ---")
    print(f"Total requests: {total_requests}")
    print(f"Number of Users: {unique_devices}")
    #print(f"Copied (duplicated) devices: {copied_devices}")
    print(f"Average requests per device: {avg_requests_per_device:.2f}")

    csv_filename = "CSV/100/100.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Data saved to {csv_filename}")

    plot_data(df)
