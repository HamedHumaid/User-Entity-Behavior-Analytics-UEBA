# Statistical User and Entity Behavior Analytics (UEBA)

## Project Flow 
1. Load raw CERT Insider Threat Dataset r4.2 (`cert/data`)
2. Extract a specific time window frame (`reduce_cert.py`)
3. Extract daily behavioral features (`daily_user_features.py`)
4. Remove malicious events from baseline period (`remove_training_insiders.py`)
5. Build user behavioral baseline (`baseline.py`)
6. Run statistical UEBA model (`src/ueba.py`)
7. Run rule-based detection (`src/rule.py`)

