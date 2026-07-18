"""
01_generate_portfolio_data.py

Generates a synthetic book of business across multiple CSMs -- account
health, ARR, renewal date, and expansion/downgrade signal -- the raw
inputs a renewal risk rollup needs. In production this would come from
your CRM (renewal dates, ARR) joined with your health-scoring system
(from the customer-health-score-model project) and your billing/usage
data (expansion or downgrade signals).

Run: python3 01_generate_portfolio_data.py
Output: portfolio.csv
"""

import numpy as np
import pandas as pd

np.random.seed(11)
N = 260  # accounts across the whole book of business

CSMS = ["Melissa McGowan", "Jordan Reyes", "Priya Nair", "Tom Alvarez"]
SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]

df = pd.DataFrame({"account_id": [f"ACCT-{i:04d}" for i in range(N)]})
df["csm"] = np.random.choice(CSMS, N, p=[0.3, 0.25, 0.25, 0.2])
df["segment"] = np.random.choice(SEGMENTS, N, p=[0.45, 0.35, 0.20])

arr_base = {"SMB": 12000, "Mid-Market": 45000, "Enterprise": 140000}
df["arr"] = df["segment"].map(lambda s: np.round(
    np.random.lognormal(np.log(arr_base[s]), 0.5), -2)).clip(2000, 900000)

# Health score: reuse the same latent-health approach as the health score project
true_health = np.random.beta(2.2, 2.0, N)
df["health_score"] = np.clip(true_health * 100 + np.random.normal(0, 6, N), 1, 99).round(1)

def band(score):
    if score >= 75: return "Healthy"
    if score >= 50: return "Neutral"
    if score >= 30: return "At Risk"
    return "Critical"

df["health_band"] = df["health_score"].apply(band)

# Renewal date: days from today, spread across the next 12 months
df["days_to_renewal"] = np.random.randint(1, 365, N)

# Expansion/downgrade signal: healthier accounts more likely to expand,
# unhealthy accounts more likely to be flagged for downgrade risk
df["expansion_signal"] = np.random.binomial(1, np.clip(true_health * 0.4, 0, 1))
df["downgrade_signal"] = np.random.binomial(1, np.clip((1 - true_health) * 0.25, 0, 1))

# Exec sponsor engagement -- a leading indicator often missing from pure usage data
df["exec_sponsor_engaged"] = np.random.binomial(1, np.clip(0.25 + true_health * 0.5, 0, 1))

df.to_csv("portfolio.csv", index=False)
print(f"Generated portfolio of {len(df)} accounts across {df['csm'].nunique()} CSMs -> portfolio.csv")
print(f"Total book ARR: ${df['arr'].sum():,.0f}")
print(df.groupby("csm")["arr"].sum().apply(lambda x: f"${x:,.0f}"))
