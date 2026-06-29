# Statistical UEBA
This is an experiment derived from the following thesis question : To what extent does a Statistical-UEBA detection system outperform a Rule-Based detection system in reducing false positive alerts and improving overall detection using CERT Insider Threat Dataset. 
## Project Flow 
1. Load raw CERT Insider Threat Dataset r4.2 (`cert/data`)
2. Extract a specific time window frame (`reduce_cert.py`)
3. Extract daily behavioral features (`daily_user_features.py`)
4. Remove malicious events from baseline period (`remove_training_insiders.py`)
5. Build user behavioral baseline (`baseline.py`)
6. Run statistical UEBA model (`src/ueba.py`)
7. Run rule-based detection (`src/rule.py`)

