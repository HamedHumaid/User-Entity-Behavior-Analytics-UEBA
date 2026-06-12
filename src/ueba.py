import pandas as pd
import numpy as np
import os

# CONFIG
base_path = r"cert\data"
output_path = r"output"
features_path = os.path.join(base_path, "features")
os.makedirs(features_path, exist_ok=True)
os.makedirs(output_path, exist_ok=True)

FEATURES_FILE = os.path.join(features_path, "daily_user_features.csv")
BASELINE_FILE = os.path.join(features_path, "user_behavior_baseline.csv")

DAILY_OUTPUT_FILE = os.path.join(output_path, "ueba_scores.csv")

DETECT_START = pd.Timestamp("2010-09-01")
DETECT_END = pd.Timestamp("2011-03-01")

EPS = 1e-6

behavior_features = [
    "login_count",
    "after_hours_logins",
    "usb_events",
    "files_accessed",
    "unique_files",
    "websites_visited",
    "email_count",
    "email_size",
    "attachments",
    "wikileaks_visits",
    "job_site_visits",
    "keylogger_downloads"
]

feature_weights = {
    "login_count_zscore": 1.0,
    "after_hours_logins_zscore": 1.5,
    "usb_events_zscore": 2.5,
    "files_accessed_zscore": 1.5,
    "unique_files_zscore": 2.0,
    "websites_visited_zscore": 1.5,
    "email_count_zscore": 1.2,
    "email_size_zscore": 1.5,
    "attachments_zscore": 1.5,
    "wikileaks_visits_zscore": 3.0,
    "job_site_visits_zscore": 2.5,
    "keylogger_downloads_zscore": 3.0
}

# LOAD DATA
features_df = pd.read_csv(FEATURES_FILE)
baseline_df = pd.read_csv(BASELINE_FILE)

features_df["user"] = features_df["user"].astype(str).str.strip()
baseline_df["user"] = baseline_df["user"].astype(str).str.strip()

features_df["day"] = pd.to_datetime(features_df["day"], errors="coerce")

# DETECTION PERIOD
detect_df = features_df[
    (features_df["day"] >= DETECT_START) &
    (features_df["day"] <= DETECT_END)
].copy()

# MERGE BASELINE
detect_df = detect_df.merge(
    baseline_df,
    on="user",
    how="left"
)

# HANDLE MISSING BASELINES
for feature in behavior_features:
    mean_col = f"{feature}_mean"
    std_col = f"{feature}_std"

    detect_df[mean_col] = detect_df[mean_col].fillna(0)
    detect_df[std_col] = detect_df[std_col].replace(0, 1).fillna(1)

# CALCULATE Z-SCORES
zscore_cols = []

for feature in behavior_features:
    mean_col = f"{feature}_mean"
    std_col = f"{feature}_std"
    z_col = f"{feature}_zscore"

    detect_df[z_col] = (
        detect_df[feature] - detect_df[mean_col]
    ) / (detect_df[std_col] + EPS)

    detect_df[z_col] = detect_df[z_col].abs()

    zscore_cols.append(z_col)

# WEIGHTED DAILY UEBA SCORE
detect_df["ueba_score"] = 0.0

for col, weight in feature_weights.items():
    detect_df["ueba_score"] += detect_df[col] * weight

detect_df["ueba_score"] = (
    detect_df["ueba_score"] / sum(feature_weights.values())
)

# 7-DAY ROLLING SCORE
detect_df = detect_df.sort_values(["user", "day"])

detect_df["ueba_score_7d"] = (
    detect_df
    .groupby("user")["ueba_score"]
    .rolling(7, min_periods=1)
    .mean()
    .reset_index(level=0, drop=True)
)

# FINAL DAILY SCORE
detect_df["final_score"] = (
    detect_df["ueba_score"] * 0.6 +
    detect_df["ueba_score_7d"] * 0.4
)

# ROBUST NORMALIZATION
p99_score = detect_df["final_score"].quantile(0.99)

if pd.isna(p99_score) or p99_score == 0:
    detect_df["ueba_score_normalized"] = 0
else:
    detect_df["ueba_score_normalized"] = (
        detect_df["final_score"] / p99_score
    ).clip(0, 1) * 100

# DAILY RISK THRESHOLDS
p95 = detect_df["final_score"].quantile(0.95)
p99 = detect_df["final_score"].quantile(0.99)
p995 = detect_df["final_score"].quantile(0.995)

def assign_daily_risk(score):
    if score >= p995:
        return "Critical"
    elif score >= p99:
        return "High"
    elif score >= p95:
        return "Medium"
    else:
        return "Low"

detect_df["risk_level"] = detect_df["final_score"].apply(assign_daily_risk)

# TOP DAILY ANOMALIES
def top_anomalies(row):
    scores = {}

    for col in zscore_cols:
        scores[col] = row[col]

    top = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]

    return ", ".join([
        f"{k.replace('_zscore', '')}:{round(v, 2)}"
        for k, v in top
    ])

detect_df["top_anomalies"] = detect_df.apply(
    top_anomalies,
    axis=1
)

# SAVE DAILY UEBA SCORES ONLY
daily_output_cols = [
    "user",
    "day",
    "ueba_score",
    "ueba_score_7d",
    "final_score",
    "ueba_score_normalized",
    "risk_level",
    "top_anomalies"
] + behavior_features + zscore_cols

daily_df = detect_df[daily_output_cols].copy()

daily_df = daily_df.sort_values(
    by="final_score",
    ascending=False
)

daily_df.to_csv(DAILY_OUTPUT_FILE, index=False)

# PRINT RESULTS
print("UEBA scoring completed.")
print("Daily UEBA scores saved to:", DAILY_OUTPUT_FILE)

# print("\nDaily risk thresholds:")
# print("Medium >=", round(p95, 3))
# print("High >=", round(p99, 3))
# print("Critical >=", round(p995, 3))

print("\nTotal daily records scored:", len(daily_df))