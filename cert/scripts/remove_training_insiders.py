import pandas as pd

features = pd.read_csv(
    "cert\\data\\features\\daily_user_features.csv"
)
answers = pd.read_csv(
    "r4.2\\answers\\insiders.csv"
)
output_file = (
    "data\\features\\baseline_features.csv"
)

# Keep only CERT 4.2 insiders
answers.columns = answers.columns.str.strip()
features.columns = features.columns.str.strip()

answers["dataset"] = answers["dataset"].astype(str).str.strip()
answers = answers[answers["dataset"].str.contains("4.2", na=False)]

# Parse dates
features["day"] = pd.to_datetime(
    features["day"].astype(str).str.strip(),
    errors="coerce"
).dt.date

answers["start"] = pd.to_datetime(
    answers["start"].astype(str).str.strip(),
    format="mixed",
    errors="coerce"
).dt.date

answers["end"] = pd.to_datetime(
    answers["end"].astype(str).str.strip(),
    format="mixed",
    errors="coerce"
).dt.date

global_start = pd.to_datetime("2010-07-01").date()
global_end = pd.to_datetime("2010-09-01").date()

# Remove bad rows
answers = answers.dropna(subset=["user", "start", "end"])

# Merge
merged = features.merge(
    answers[["user", "start", "end"]],
    on="user",
    how="left"
)

drop_mask = (
    merged["start"].notna()
    & (merged["day"] >= merged["start"])
    & (merged["day"] <= merged["end"])
    & (merged["day"] >= global_start)
    & (merged["day"] <= global_end)
)

# Clean dataset
clean = merged.loc[~drop_mask].drop(columns=["start", "end"])

# Save
clean.to_csv(output_file, index=False)

print(f"Dropped insider rows: {drop_mask.sum()}")
print(f"Remaining rows: {len(clean)}")
print(f"Saved to {output_file}")