# Statistical User and Entity Behavior Analytics (UEBA)

## Project Desciption

This project implements a **User and Entity Behavior Analytics (UEBA)** system to detect insider threats using behavioral baselining and anomaly detection techniques. It compares a **Rule-Based Detection Engine** against a **Statistical UEBA Model** using the CERT Insider Threat Dataset v4.2.

## Problem Statement

Traditional security systems rely heavily on:

- Static thresholds
- Predefined detection rules
- Event correlation logic

### Limitations:

- Poor adaptability to unknown threats
- High false-positive rates
- Limited ability to detect insider threats

---

## Proposed Solution
This project introduces a **Statistical UEBA pipeline** that:

- Builds behavioral baselines from historical activity
- Detects deviations from normal behavior
- Assigns anomaly and risk scores to users

---

## Dataset

This project uses the:

- CERT Insider Threat Dataset v4.2  
- Carnegie Mellon University CERT Program

---

## Project Flow 

1. Load raw CERT dataset (`cert/data`)
2. Extract daily behavioral features (`daily_user_features.py`)
3. Remove malicious activities from baseline period (`remove_training_insiders.py`)
3. Build user behavioral baselines (`baseline.py`)
5. Run statistical UEBA model (`src/ueba.py`)
6. Run rule-based detection (`src/rule.py`)
7. Compare detection performance using top-k metrics.

---


## Future Improvements

- Add machine learning-based UEBA model (Isolation Forest)
- Improve feature engineering
- Enable peer group, sequence, and contexual analysis.

---
