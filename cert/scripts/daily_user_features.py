import pandas as pd
import os
from urllib.parse import urlparse

base_path = r"\cert\data"

output_path = os.path.join(base_path, "features")
os.makedirs(output_path, exist_ok=True)

# LOAD DATA
logon = pd.read_csv(os.path.join(base_path, "logon.csv"))
device = pd.read_csv(os.path.join(base_path, "device.csv"))
filelog = pd.read_csv(os.path.join(base_path, "file.csv"))
http = pd.read_csv(os.path.join(base_path, "http.csv"))
email = pd.read_csv(os.path.join(base_path, "email.csv"))

datasets = [logon, device, filelog, http, email]

# STANDARDIZE TIME
for df in datasets:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["day"] = df["date"].dt.floor("D")
    df["hour"] = df["date"].dt.hour

# LOGON FEATURES
logon["after_hours"] = (
    (logon["hour"] < 6) |
    (logon["hour"] > 22)
).astype(int)

logon_feat = logon.groupby(["user", "day"]).agg(
    login_count=("activity", "count"),
    after_hours_logins=("after_hours", "sum")
).reset_index()

# USB FEATURES
device["usb_connect"] = device["activity"].str.contains(
    "connect",
    case=False,
    na=False
).astype(int)


device_feat = device.groupby(["user", "day"]).agg(
    usb_events=("usb_connect", "sum")
).reset_index()

# FILE FEATURES
file_feat = filelog.groupby(["user", "day"]).agg(
    files_accessed=("filename", "count"),
    unique_files=("filename", "nunique")
).reset_index()

# WEB FEATURES
def extract_domain(url):
    try:
        return urlparse(str(url)).netloc.lower()
    except Exception:
        return ""

http["domain"] = http["url"].apply(extract_domain)

http["wikileaks_visits"] = http["url"].str.contains(
    "wikileaks.org",
    case=False,
    na=False
).astype(int)

http["job_site_visits"] = http["url"].str.contains(
    r"linkedin\.com|indeed\.com|monster\.com|glassdoor\.com|careerbuilder\.com",
    case=False,
    na=False
).astype(int)

http["keylogger_downloads"] = http["url"].str.contains(
    r"keylogger|keystroke|spyware|refog|elitekeylogger|revealerkeylogger",
    case=False,
    na=False
).astype(int)

web_feat = http.groupby(["user", "day"]).agg(
    websites_visited=("url", "count"),
    unique_domains=("domain", "nunique"),
    wikileaks_visits=("wikileaks_visits", "sum"),
    job_site_visits=("job_site_visits", "sum"),
    keylogger_downloads=("keylogger_downloads", "sum")
).reset_index()

# EMAIL FEATURES
email["size"] = pd.to_numeric(email["size"], errors="coerce").fillna(0)

if "attachments" not in email.columns:
    email["attachments"] = 0

email["attachments"] = pd.to_numeric(
    email["attachments"],
    errors="coerce"
).fillna(0)

email_feat = email.groupby(["user", "day"]).agg(
    email_count=("id", "count"),
    email_size=("size", "sum"),
    attachments=("attachments", "sum")
).reset_index()

# MERGE ALL FEATURES
features_df = logon_feat.copy()

for feat in [device_feat, file_feat, web_feat, email_feat]:
    features_df = features_df.merge(
        feat,
        on=["user", "day"],
        how="outer"
    )

features_df = features_df.fillna(0)

# SAVE FEATURE DATASET
features_output = os.path.join(output_path, "daily_user_features.csv")
features_df.to_csv(features_output, index=False)

print("Feature extraction completed.")
print("Saved to:", features_output)
