import os
import pandas as pd

ORIGINAL_DIR = "r4.2"
REDUCED_DIR = "data"

START_DATE = "2010-07-01"
END_DATE = "2011-03-01"

# Make sure to drop content column from http and email 
FILES = {
    "logon.csv": "date",
    "device.csv": "date",
    "file.csv": "date",
    "email.csv": "date",
    "http.csv": "date",
}

os.makedirs(REDUCED_DIR, exist_ok=True)


def reduce_csv(filename, date_col):
    input_path = os.path.join(ORIGINAL_DIR, filename)
    output_path = os.path.join(REDUCED_DIR, filename)

    if not os.path.exists(input_path):
        print(f"[WARN] Missing file: {filename}")
        return

    print(f"[INFO] Reading {filename}")
    df = pd.read_csv(input_path)

    if date_col not in df.columns:
        print(f"[WARN] No date column in {filename}")
        return

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    reduced = df[
        (df[date_col] >= START_DATE) &
        (df[date_col] < END_DATE)
    ]

    reduced.to_csv(output_path, index=False)
    print(f"[INFO] Saved {filename}: {len(reduced)} rows")


for filename, date_col in FILES.items():
    reduce_csv(filename, date_col)
