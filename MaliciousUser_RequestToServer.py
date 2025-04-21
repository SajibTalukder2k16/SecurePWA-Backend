#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 02:35:15 2025
@author: sajib
"""

import os
import pandas as pd
import requests
import time
import csv
import matplotlib.pyplot as plt

# ===================== Configurable Parameters =====================
num_users = 20
devices = 5
threshold = 30

API_URL = "http://localhost:5002/getQuote"


# ===================== Dynamic Paths ================================
base_dir = f"DataSetForSmallNumber/Malicious/Input/User_{num_users}/Attack_Device_{devices}"
input_csv = os.path.join(base_dir, f"{num_users}_{devices}.csv")
output_dir = os.path.join(base_dir, f"Output/{threshold}")
output_csv = os.path.join(output_dir, f"U{num_users}_D{devices}_T{threshold}_output.csv")
plot_path = os.path.join(output_dir, f"Responses_U{num_users}_D{devices}_T{threshold}.png")

os.makedirs(output_dir, exist_ok=True)

# ===================== Load Data ================================
df = pd.read_csv(input_csv)

# ===================== Initialize Output File ====================
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["user_id", "deviceID", "timestamp", "response_status", "response_message", "raw_response"])

# ===================== API Call Loop =============================
responses = []
for index, row in df.iterrows():
    payload = {
        "param": str(row["encryptedParam"]).strip(),
        "reSubmit": False
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=5)
        print(f"Response [{index+1}/{len(df)}]: Status Code: {response.status_code}, Response Text: {response.text}")
        
        if not response.text.strip():
            raise ValueError("Empty response from server")

        response_data = response.json()
        status_code = response.status_code
        message = response_data.get("message", response_data.get("error", "Unknown Error"))
        
    except requests.exceptions.RequestException as e:
        status_code = "ERROR"
        message = str(e)
        response_data = None

    except ValueError as ve:
        status_code = "ERROR"
        message = str(ve)
        response_data = None

    # Write response
    row_data = [row["user_id"], row["deviceId"], row["timestamp"], status_code, message, response_data]
    responses.append(row_data)

    with open(output_csv, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row_data)

    time.sleep(0.1)  # Prevent overloading

print(f"\nAll API responses saved to {output_csv}")

# ===================== Analysis & Plotting =======================
response_df = pd.DataFrame(responses, columns=["user_id", "deviceID", "timestamp", "response_status", "response_message", "raw_response"])

success_count = sum(response_df["response_status"] == 200)
failure_count = sum(response_df["response_status"] != 200)

plt.figure(figsize=(8, 6))
plt.bar(["Success", "Failure"], [success_count, failure_count], color=['green', 'red'])
plt.xlabel("Response Type")
plt.ylabel("Count")
plt.title("API Request Success vs Failure Count")
plt.savefig(plot_path)
plt.show()

# ===================== Summary Report ============================
response_df['normalized_message'] = response_df['response_message'].str.lower().str.strip()

successful_requests = (response_df['normalized_message'] == 'success').sum()
existing_data = (response_df['normalized_message'] == 'already existing data').sum()
access_limit_reached = (response_df['normalized_message'] == 'access limit reached').sum()
expired = (response_df['normalized_message'] == 'expired').sum()
total_requests = len(response_df)

print("\n--- Request Summary ---")
print(f"Total Requests: {total_requests}")
print(f"Successful Requests: {successful_requests}")
print(f"Already Existing Data: {existing_data}")
print(f"Access Limit Reached: {access_limit_reached}")
print(f"Expired: {expired}")
