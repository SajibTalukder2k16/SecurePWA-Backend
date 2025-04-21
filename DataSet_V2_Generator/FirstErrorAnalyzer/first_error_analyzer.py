#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 15:59:58 2025

@author: sajib
"""

import pandas as pd

# === Configuration ===

input_csv = "V1_500_10/U500_D10_T30_output.csv"  # Replace with your actual file path
output_excel = "V1_500_10/output/M_500_10_30_first_error_requests_with_number.xlsx"


# === Load Data ===
df = pd.read_csv(input_csv)

# Add a request number based on appearance in the dataset per user
df["request_number"] = df.groupby("user_id").cumcount() + 1

# Get total requests per user
request_counts = df["user_id"].value_counts().reset_index()
request_counts.columns = ["user_id", "total_requests"]

# Find first error based on dataset order (not timestamp)
first_errors = (
    df[df["response_status"] != 200]
    .groupby("user_id", as_index=False)
    .first()
)

# Extract only relevant columns
first_errors = first_errors[[
    "user_id", "timestamp", "response_status", "response_message", "request_number"
]]

# Merge with total request counts
final_result = pd.merge(first_errors, request_counts, on="user_id")

# Rename and reorder columns
final_result.rename(columns={"request_number": "first_error_request_number"}, inplace=True)
final_result = final_result[[
    "user_id", "total_requests", "first_error_request_number", "timestamp", "response_status", "response_message"
]]

# Save to Excel
final_result.to_excel(output_excel, index=False)
print(f"Output saved to: {output_excel}")
