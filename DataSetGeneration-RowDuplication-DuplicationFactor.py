#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 15 16:19:29 2025

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

def generate_data(num_devices, num_unique_entries, min_requests, max_requests, duplication_factor):
    data_list = []
    current_time = datetime.datetime.now()
    end_time = current_time + datetime.timedelta(hours=20)
    
    unique_entries = []
    for _ in range(num_unique_entries):
        device_id = generate_device_id()
        timestamp = current_time + datetime.timedelta(seconds=random.randint(0, 72000))
        hour = timestamp.hour
        
        raw_data = f"{int(timestamp.timestamp() * 1000)}@PWA{device_id}"
        encrypted_param = mcrypt.encrypt(raw_data)
        
        # Verify encryption correctness
        assert mcrypt.decrypt(encrypted_param) == raw_data, "Encryption/Decryption mismatch!"
        
        unique_entries.append([device_id, int(timestamp.timestamp() * 1000), hour, raw_data, encrypted_param])
    
    # Duplicate entire rows
    for _ in range(num_devices):
        row = random.choice(unique_entries)
        for _ in range(duplication_factor):
            data_list.append(row)
    
    df = pd.DataFrame(data_list, columns=["deviceId", "timestamp", "hour", "rawData", "encryptedParam"])
    return df

def plot_data(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['hour'] = df['timestamp'].dt.hour
    
    # Aggregate request count per hour
    request_counts = df.groupby('hour').size()
    
    plt.figure(figsize=(10, 5))
    plt.plot(request_counts.index, request_counts.values, marker='o', linestyle='-', color='b')
    plt.xlabel("Hour")
    plt.ylabel("Number of Requests")
    plt.title("Request Distribution Over 20 Hours (With Fully Duplicated Rows)")
    plt.xticks(range(0, 24))
    plt.grid()
    plt.show()
    
    # Plot first two unique devices
    unique_devices = df['deviceId'].unique()[:2]
    for device in unique_devices:
        device_df = df[df['deviceId'] == device]
        request_counts_device = device_df.groupby('hour').size()
        
        plt.figure(figsize=(10, 5))
        plt.plot(request_counts_device.index, request_counts_device.values, marker='o', linestyle='-', alpha=0.7)
        plt.xlabel("Hour")
        plt.ylabel("Number of Requests")
        plt.title(f"Request Distribution for Device {device}")
        plt.xticks(range(0, 24))
        plt.grid()
        plt.show()

if __name__ == "__main__":
    num_devices = int(input("Enter total number of device entries: "))
    num_unique_entries = int(input("Enter number of unique device ID & timestamp combinations: "))
    min_requests = int(input("Enter minimum requests per device: "))
    max_requests = int(input("Enter maximum requests per device: "))
    duplication_factor = int(input("Enter row duplication factor: "))
    
    df = generate_data(num_devices, num_unique_entries, min_requests, max_requests, duplication_factor)
    csv_filename = "CSV/row-duplicate-1.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Data saved to {csv_filename}")
    
    plot_data(df)