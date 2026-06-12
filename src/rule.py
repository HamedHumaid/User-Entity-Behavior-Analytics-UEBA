import pandas as pd
import numpy as np


class RuleEngine:
    def __init__(self):
        self.rules = [
            self.rule_after_hours_usb,
            self.rule_high_usb_usage,
            self.rule_keylogger_mass_email,
            self.rule_high_web_and_usb,
        ]

        self.rule_weights = {
            "Scenario 1: after-hours USB use with WikiLeaks upload": 4,
            "Scenario 2: job search followed by high USB activity": 3,
            "Scenario 3: keylogger activity with abnormal email behavior": 5,
            "High web and usb activity": 2,
        }

    def evaluate(self, row):
        alerts = []

        for rule in self.rules:
            result = rule(row)
            if result:
                alerts.append(result)

        risk_level = "ALERT" if alerts else "NORMAL"
        rule_count = len(alerts)
        rule_score = sum(self.rule_weights.get(alert, 0) for alert in alerts)

        return pd.Series({
            "risk_level": risk_level,
            "triggered_rules": "; ".join(alerts),
            "rule_count": rule_count,
            "rule_score": rule_score
        })

    def rule_after_hours_usb(self, row):
        if (
            row["after_hours_logins"] > 0 and
            row["usb_events"] > 0 and
            row["wikileaks_visits"] > 0
        ):
            return "Scenario 1: after-hours USB use with WikiLeaks upload"

    def rule_high_usb_usage(self, row):
        if (
            row["usb_events"] > 3 and
            row["job_site_visits"] > 0
        ):
            return "Scenario 2: job search followed by high USB activity"

    def rule_keylogger_mass_email(self, row):
        if (
            row["keylogger_downloads"] > 0 and
            (
                row["email_count"] > 0 or
                row["attachments"] > 0
            )
        ):
            return "Scenario 3: keylogger activity with abnormal email behavior"

    def rule_high_web_and_usb(self, row):
        if (
            row["websites_visited"] > 100 and
            row["usb_events"] > 5
        ):
            return "High web and usb activity"


def run_rule_engine(input_csv, output_csv="alerts.csv"):
    df = pd.read_csv(input_csv)

    df["day"] = pd.to_datetime(df["day"])

    df = df[
        (df["day"] >= "2010-09-01") &
        (df["day"] <= "2011-03-01")
    ]

    numeric_cols = [
        "login_count",
        "after_hours_logins",
        "usb_events",
        "files_accessed",
        "unique_files",
        "websites_visited",
        "unique_domains",
        "wikileaks_visits",
        "job_site_visits",
        "keylogger_downloads",
        "email_count",
        "email_size",
        "attachments",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    engine = RuleEngine()
    results = df.apply(engine.evaluate, axis=1)

    output = pd.concat([df, results], axis=1)

    alerts = output[output["risk_level"] != "NORMAL"].copy()

    alerts = alerts.sort_values(
        by=["rule_score", "rule_count", "day"],
        ascending=[False, False, True]
    )

    alerts["rank"] = range(1, len(alerts) + 1)

    alerts.to_csv(output_csv, index=False)

    print("Rule engine completed.")
    print(f"Total records: {len(output)}")
    print(f"Alerts generated: {len(alerts)}")
    print(f"Output saved to: {output_csv}")

    return output, alerts


if __name__ == "__main__":
    output, alerts = run_rule_engine(
        input_csv="cert\\data\\features\\daily_user_features.csv",
        output_csv="ueba\\output\\rule_alerts.csv"
    )