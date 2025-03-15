import pandas as pd
import random
import string
import time
import datetime
from Crypto.Cipher import AES
import binascii

# AES encryption class
class MCrypt:
    def __init__(self, secret_key, iv):
        self.secret_key = secret_key.encode('utf-8')
        self.iv = iv.encode('utf-8')
        self.cipher = AES.new(self.secret_key, AES.MODE_CBC, self.iv)

    def encrypt(self, raw_data):
        raw_data = raw_data + (16 - len(raw_data) % 16) * chr(16 - len(raw_data) % 16)
        raw_data = raw_data.encode('utf-8')
        encrypted = self.cipher.encrypt(raw_data)
        return binascii.hexlify(encrypted).decode('utf-8')

# Generate random device ID
def generate_device_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# Define encryption keys
SECRET_KEY = "lhoiyrtevcyrtfvs"
IV = "usrqutsvbxcjpoyt"
mcrypt = MCrypt(SECRET_KEY, IV)

def generate_data(num_devices, num_requests):
    data_list = []
    current_time = datetime.datetime.now()
    end_time = current_time + datetime.timedelta(hours=10)
    
    while current_time <= end_time:
        hour = current_time.hour
        if 8 <= hour <= 10 or 17 <= hour <= 19:  # Peak hours
            requests_per_hour = int(num_requests * 1.5)  # Increase load
        else:  # Off-peak hours
            requests_per_hour = num_requests
        
        for _ in range(num_devices):
            device_id = generate_device_id()
            for _ in range(requests_per_hour):
                timestamp = int(current_time.timestamp() * 1000)
                raw_data = f"{timestamp}@PWA{device_id}"
                encrypted_param = mcrypt.encrypt(raw_data)
                data_list.append([device_id, timestamp, hour, raw_data, encrypted_param])
        
        current_time += datetime.timedelta(minutes=10)  # Move forward in time
    
    df = pd.DataFrame(data_list, columns=["deviceId", "timestamp", "hour", "rawData", "encryptedParam"])
    return df

if __name__ == "__main__":
    num_devices = int(input("Enter number of devices: "))
    num_requests = int(input("Enter number of requests per device per hour: "))
    df = generate_data(num_devices, num_requests)
    csv_filename = "encrypted_params.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Data saved to {csv_filename}")
