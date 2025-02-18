import pandas as pd
import requests
import time
import csv
import pdb  # Import Python debugger

# Flask API URL
API_URL = "http://localhost:5001/getQuote"

# Load the encrypted dataset
csv_file = "encrypted_device_timestamps_app_usage_next_2_to_20_hours.csv"  # Change if needed
df = pd.read_csv(csv_file)

# Output CSV for storing API responses
output_file = "api_responses.csv"

# Initialize CSV file with headers
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["deviceID", "timestamp", "response_status", "response_message", "raw_response"])

# Process each row and send API requests
for index, row in df.iterrows():
    payload = {
        "enM": str(row["timestamp"]).strip(),  # Encrypted Timestamp
        "enI": str(row["deviceID"]).strip(),  # Encrypted Device ID
        "reSubmit": False
    }

    headers = {
        "Content-Type": "application/json"
    }

    # Debugger - Stops execution for inspection


    try:
        # Send POST request
        response = requests.post(API_URL, json=payload, headers=headers, timeout=5)
        
        # Log raw response
        print(f"Response [{index+1}/{len(df)}]: Status Code: {response.status_code}, Response Text: {response.text}")

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

    # Append response to CSV
    with open(output_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([row["deviceID"], row["timestamp"], status_code, message, response_data])

    # Delay to prevent overwhelming the server
    time.sleep(0.1)

print(f"\nAll API responses saved to {output_file}")