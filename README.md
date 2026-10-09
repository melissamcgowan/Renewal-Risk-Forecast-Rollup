# Renewal Risk & Forecast Rollup

A portfolio project that rolls up account-level health and renewal data
into a leadership-ready view of revenue at risk -- the report a CS
leader would bring into a staff meeting, QBR-of-QBRs, or board update.

## Why this project

Most renewal forecasts just show "how much ARR renews this quarter."
That's not the useful number -- the useful number is how much of that
ARR is actually at risk, and where. This project takes the same health
signals from the customer-health-score-model project and rolls them up
across a full book of business, weighted by churn risk, broken out by
renewal window, CSM, segment, and individual flagged accounts.

Try it live: https://melissamcgowan.github.io/Renewal-Risk-Forecast-Rollup/

## What it does

1. **`01_generate_portfolio_data.py`** -- Generates a synthetic book of
   260 accounts across 4 CSMs: ARR, segment, health score/band, days to
   renewal, and expansion/downgrade signals. (In production: joined from
   your CRM's renewal dates, your health-scoring system, and usage/
   billing data.)

2. **`02_renewal_risk_rollup.py`** -- Applies a risk-weighting model
   (health band -> assumed churn probability, adjustable and calibrated
   against real churn history) to convert raw ARR into risk-weighted
   "ARR at risk." Produces three views: rollup by renewal window,
   breakdown by CSM, and a flagged list of the highest-risk individual
   accounts.

3. **`03_visualize.py`** -- Builds a four-panel leadership dashboard:
   total vs. at-risk ARR by window, at-risk ARR by CSM, account
   distribution by health band, and at-risk ARR by segment.

4. **`04_build_webapp.py`** + **`webapp_template.html`** -- Builds
   `index.html`, an interactive, self-contained version of the dashboard
   (no server, no external libraries). Filter by renewal window, CSM,
   segment, and health band, click any bar to drill in, and move the
   churn-probability sliders to see how the forecast changes under
   different assumptions. Two-layer design: the Python script is the data
   layer and the template is the presentation layer, so a live CRM export
   can replace just `read_portfolio()`.

## Results

On the sample book of business (260 accounts, $14.5M total ARR):
- **$1.35M of ARR at risk** in the next 90 days (29.4% of the $4.6M
  renewing in that window)
- Risk concentration varies meaningfully by CSM (16%-41% of their
  90-day book at risk) -- the kind of gap that's invisible in a simple
  "ARR renewing" report but obvious once risk-weighted
- Top 10 flagged accounts surfaced automatically, ranked by ARR at risk,
  ready to route to CSMs or leadership for proactive outreach

## How to run it

```bash
pip install pandas matplotlib numpy
python3 01_generate_portfolio_data.py  # generates portfolio.csv
python3 02_renewal_risk_rollup.py      # generates renewal_rollup.csv + console summary
python3 03_visualize.py                # generates renewal_risk_dashboard.png
python3 04_build_webapp.py             # generates index.html (open it in a browser)
```

## How this maps to a real CS org

- Replace `RISK_WEIGHTS` with actual churn-rate-by-health-band numbers
  from your own historical data -- exactly what the churn model in the
  customer-health-score-model project
  produces. These two projects are designed to plug into each other:
  swap the static weights for that model's live predicted probabilities.
- Run this on a schedule (weekly/monthly) and track how the at-risk
  total trends over time -- the trend line matters as much as the
  snapshot.
- Feed the CSM-level breakdown into 1:1s to guide coaching and
  prioritization, and the flagged-account list into a save-play workflow.

## Extending this further

- Add a trend view showing how total ARR-at-risk has moved over the
  last several rollups, not just a single snapshot.
- Weight the risk model by segment as well as health band -- Enterprise
  churn often has different drivers and different assumed probabilities
  than SMB.
- Export the CSM breakdown as an auto-generated leadership summary
  (reusing the PDF generation approach from the QBR automation project).
