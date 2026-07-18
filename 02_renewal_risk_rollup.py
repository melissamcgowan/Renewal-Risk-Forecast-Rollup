"""
02_renewal_risk_rollup.py

Turns raw account-level data into a leadership-ready renewal risk view:
a rolling 90-day (and 180-day) forward look at ARR up for renewal,
weighted by churn risk, so leadership sees "how much revenue is
actually at risk" rather than just "how much ARR renews this quarter."

The risk weighting is a simple, explainable heuristic (health band ->
assumed churn probability) so it's easy to defend in a business review.
For a data-driven version, swap RISK_WEIGHTS for the trained churn
model's predicted probabilities from the customer-health-score-model
project -- the two projects are designed to plug into each other.

Run: python3 02_renewal_risk_rollup.py
Outputs: renewal_rollup.csv, console summary
"""

import pandas as pd

df = pd.read_csv("portfolio.csv")

# Assumed churn probability by health band -- calibrate this against your
# own historical churn-by-band data (exactly what the churn model in the
# health-score project produces).
RISK_WEIGHTS = {
    "Healthy": 0.02,
    "Neutral": 0.10,
    "At Risk": 0.35,
    "Critical": 0.65,
}

df["assumed_churn_prob"] = df["health_band"].map(RISK_WEIGHTS)
df["arr_at_risk"] = (df["arr"] * df["assumed_churn_prob"]).round(0)

# Adjust risk up slightly for accounts with a downgrade signal and no
# exec sponsor -- these are leading indicators health score alone can miss
df.loc[(df["downgrade_signal"] == 1) & (df["exec_sponsor_engaged"] == 0), "arr_at_risk"] *= 1.15

def renewal_window(days):
    if days <= 90:
        return "Next 90 days"
    elif days <= 180:
        return "91-180 days"
    else:
        return "180+ days"

df["renewal_window"] = df["days_to_renewal"].apply(renewal_window)

# ---------------------------------------------------------------------
# Leadership rollup: ARR and risk by renewal window
# ---------------------------------------------------------------------
window_order = ["Next 90 days", "91-180 days", "180+ days"]
rollup = (df.groupby("renewal_window")
            .agg(accounts=("account_id", "count"),
                 total_arr=("arr", "sum"),
                 arr_at_risk=("arr_at_risk", "sum"))
            .reindex(window_order))
rollup["pct_arr_at_risk"] = (rollup["arr_at_risk"] / rollup["total_arr"] * 100).round(1)

print("=== Renewal Forecast Rollup (by window) ===")
print(rollup.to_string(formatters={
    "total_arr": "${:,.0f}".format,
    "arr_at_risk": "${:,.0f}".format,
    "pct_arr_at_risk": "{}%".format,
}))

# ---------------------------------------------------------------------
# By CSM: who's carrying the most risk in the next 90 days
# ---------------------------------------------------------------------
next_90 = df[df["renewal_window"] == "Next 90 days"]
by_csm = (next_90.groupby("csm")
                  .agg(accounts=("account_id", "count"),
                       arr=("arr", "sum"),
                       arr_at_risk=("arr_at_risk", "sum"))
                  .sort_values("arr_at_risk", ascending=False))
by_csm["pct_at_risk"] = (by_csm["arr_at_risk"] / by_csm["arr"] * 100).round(1)

print("\n=== Next-90-Day Renewal Risk by CSM ===")
print(by_csm.to_string(formatters={
    "arr": "${:,.0f}".format,
    "arr_at_risk": "${:,.0f}".format,
    "pct_at_risk": "{}%".format,
}))

# ---------------------------------------------------------------------
# Top individual accounts to flag for exec attention
# ---------------------------------------------------------------------
top_flags = (next_90[next_90["health_band"].isin(["At Risk", "Critical"])]
             .sort_values("arr_at_risk", ascending=False)
             .head(10))

print("\n=== Top 10 Accounts to Flag (Next 90 Days, At Risk / Critical) ===")
print(top_flags[["account_id", "csm", "segment", "arr", "health_band",
                  "days_to_renewal", "arr_at_risk"]].to_string(index=False,
      formatters={"arr": "${:,.0f}".format, "arr_at_risk": "${:,.0f}".format}))

df.to_csv("renewal_rollup.csv", index=False)
print("\nSaved renewal_rollup.csv")
