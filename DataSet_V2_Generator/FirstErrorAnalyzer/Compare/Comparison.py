#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 15:05:42 2025

@author: sajib
"""

import pandas as pd
import matplotlib.pyplot as plt

# Load the data
benign_df = pd.read_excel("B_500_30_first_error_requests_with_number.xlsx")
malicious_df = pd.read_excel("M_500_10_30_first_error_requests_with_number.xlsx")

# Filter out benign users with first error < 30
benign_df = benign_df[benign_df["first_error_request_number"] >= 30]

# Sort by user_id
benign_sorted = benign_df.sort_values("user_id")
malicious_sorted = malicious_df.sort_values("user_id")

# Plot
plt.figure(figsize=(14, 6))

# Total Requests (Benign)
plt.plot(
    benign_sorted["user_id"],
    benign_sorted["total_requests"],
    label="Number of Request Per User",
    color="cyan",
    linestyle="--",
    marker="s"
)

# First Error Request (Benign)
plt.plot(
    benign_sorted["user_id"],
    benign_sorted["first_error_request_number"],
    label="First Error for Normal User)",
    color="blue",
    marker="o"
)

# First Error Request (Malicious)
plt.plot(
    malicious_sorted["user_id"],
    malicious_sorted["first_error_request_number"],
    label="First Error for Malicious User",
    color="red",
    marker="x"
)

# Labels and styling
plt.xlabel("User ID")
plt.ylabel("Request Count")
plt.title("Comparison of Total and First Error Requests (Benign ≥ 30)")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save and show
plt.savefig("benign_malicious_first_error_total_requests_filtered.pdf")
plt.show()
