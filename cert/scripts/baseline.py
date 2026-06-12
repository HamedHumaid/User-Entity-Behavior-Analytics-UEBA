import pandas as pd
import os

# CONFIG
base_path = r"cert\data"

features_path = os.path.join(base_path, "features")
os.makedirs(features_path, exist_ok=True)

FEATURES_FILE = os.path.join(features_path, "baseline_features.csv")
BASELINE_OUTPUT_FILE = os.path.join(features_path, "user_behavior_baseline.csv")

BASELINE_START = pd.Timestamp("2010-07-01")
BASELINE_END = pd.Timestamp("2010-09-01")

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
    "keylogger_downloads",
]

# LOAD FEATURES
features_df = pd.read_csv(FEATURES_FILE)
features_df["day"] = pd.to_datetime(features_df["day"], errors="coerce")

# BASELINE PERIOD
baseline_df = features_df[
    (features_df["day"] >= BASELINE_START) &
    (features_df["day"] <= BASELINE_END)
].copy()

# BUILD USER BASELINES
baseline_stats = baseline_df.groupby("user")[behavior_features].agg(["mean", "std"])

baseline_stats.columns = [
    f"{feature}_{stat}"
    for feature, stat in baseline_stats.columns
]

baseline_stats = baseline_stats.reset_index()

# FIX ZERO STD
for feature in behavior_features:
    std_col = f"{feature}_std"

    baseline_stats[std_col] = (
        baseline_stats[std_col]
        .replace(0, 1)
        .fillna(1)
    )

baseline_stats.to_csv(BASELINE_OUTPUT_FILE, index=False)

print("User behavior baseline completed.")
print("Saved to:", BASELINE_OUTPUT_FILE)