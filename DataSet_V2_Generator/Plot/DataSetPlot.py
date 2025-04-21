#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 14:41:25 2025

@author: sajib
"""
import pandas as pd
import matplotlib.pyplot as plt

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


df = pd.read_csv("500_10.csv")
plot_data(df)