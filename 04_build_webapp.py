"""
04_build_webapp.py

Builds the interactive version of the renewal risk rollup: a single,
self-contained index.html (no server, no external libraries) that you can
open locally or host on GitHub Pages.

Two-layer design: this script is the data layer. It reads portfolio.csv
and the default risk assumptions, and embeds them into webapp_template.html,
which is the presentation layer. To point the page at live data later,
replace only the read_portfolio() step (for example, a CRM export or an
API call) and keep the template as is.

The page recalculates risk in the browser, so viewers can change the churn
assumptions and filters and see the forecast move.

Run: python3 04_build_webapp.py
Output: index.html
"""

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent

# Keep these in sync with RISK_WEIGHTS and the uplift rule in
# 02_renewal_risk_rollup.py. They are only the starting values in the page.
DEFAULT_WEIGHTS = {"Healthy": 0.02, "Neutral": 0.10, "At Risk": 0.35, "Critical": 0.65}
DOWNGRADE_NO_SPONSOR_UPLIFT = 1.15


def read_portfolio():
    """Data layer: swap this for a CRM export or API call to go live."""
    df = pd.read_csv(HERE / "portfolio.csv")
    return [
        {
            "id": r.account_id,
            "csm": r.csm,
            "segment": r.segment,
            "arr": int(r.arr),
            "score": float(r.health_score),
            "band": r.health_band,
            "days": int(r.days_to_renewal),
            "expansion": int(r.expansion_signal),
            "downgrade": int(r.downgrade_signal),
            "sponsor": int(r.exec_sponsor_engaged),
        }
        for r in df.itertuples()
    ]


def main():
    payload = {
        "rows": read_portfolio(),
        "weights": DEFAULT_WEIGHTS,
        "uplift": DOWNGRADE_NO_SPONSOR_UPLIFT,
    }
    template = (HERE / "webapp_template.html").read_text(encoding="utf-8")
    html = template.replace("__DATA__", json.dumps(payload, separators=(",", ":")))
    (HERE / "index.html").write_text(html, encoding="utf-8")
    print(f"Built index.html with {len(payload['rows'])} accounts")


if __name__ == "__main__":
    main()
