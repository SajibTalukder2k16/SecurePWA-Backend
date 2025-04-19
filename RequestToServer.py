#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 15 13:19:45 2025

@author: sajib
"""

import pandas as pd
import requests
import time
import csv
import matplotlib.pyplot as plt

# Flask API URL
API_URL = "http://localhost:5001/getQuote"

# Load the encrypted dataset
csv_file = "DataSet_V2_Generator/Benign/CSV/500/500.csv" # Change if needed
df = pd.read_csv(csv_file)

# Output CSV for storing API responses
output_file = "DataSet_V2_Generator/Benign/CSV/500/Output/30/500_30_output.csv"


# Initialize CSV file with headers
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["user_id", "deviceID", "timestamp", "response_status", "response_message", "raw_response"])

# Process each row and send API requests
responses = []
for index, row in df.iterrows():
    payload = {
        "param": str(row["encryptedParam"]).strip(),  # Encrypted parameter
        "reSubmit": False
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Send POST request
        response = requests.post(API_URL, json=payload, headers=headers, timeout=5)
        
        # Log raw response
        #print(f"Response [{index+1}/{len(df)}]: Status Code: {response.status_code}, Response Text: {response.text}")

        # Check if response is empty
        if not response.text.strip():
            raise ValueError("Empty response from server")

        # Try parsing JSON
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

    # Append response to CSV and list
    responses.append([row["user_id"],row["deviceId"], row["timestamp"], status_code, message, response_data])
    
    with open(output_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([row["user_id"],row["deviceId"], row["timestamp"], status_code, message, response_data])
    
    # Delay to prevent overwhelming the server
    time.sleep(0.1)

print(f"\nAll API responses saved to {output_file}")

# Convert to DataFrame for plotting
response_df = pd.DataFrame(responses, columns=["user_id","deviceID", "timestamp", "response_status", "response_message", "raw_response"])

# Count successful and failed requests
success_count = sum(response_df["response_status"] == 200)
failure_count = sum(response_df["response_status"] != 200)

# Plot the results
plt.figure(figsize=(8, 6))
plt.bar(["Success", "Failure"], [success_count, failure_count], color=['green', 'red'])
plt.xlabel("Response Type")
plt.ylabel("Count")
plt.title("API Request Success vs Failure Count")
plt.savefig("DataSet_V2_Generator/Benign/CSV/500/Output/30/result_500_30.png")
plt.show()

# Normalize case to handle inconsistencies
response_df['normalized_message'] = response_df['response_message'].str.lower().str.strip()

# Count each response category
successful_requests = (response_df['normalized_message'] == 'success').sum()
existing_data = (response_df['normalized_message'] == 'already existing data').sum()
access_limit_reached = (response_df['normalized_message'] == 'access limit reached').sum()
expired = (response_df['normalized_message'] == 'Expired').sum()
total_requests = len(response_df)

# Print summary
print("\n--- Request Summary ---")
print(f"Total Requests: {total_requests}")
print(f"Successful Requests: {successful_requests}")
print(f"Already Existing Data: {existing_data}")
print(f"Access Limit Reached: {access_limit_reached}")
print(f"Expired: {expired}")