"""
03_visualize.py

Builds a leadership-facing dashboard image summarizing renewal risk
across the book of business -- the kind of visual you'd drop into a
board deck or a leadership staff meeting.

Run: python3 03_visualize.py
Output: renewal_risk_dashboard.png
"""

import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

df = pd.read_csv("renewal_rollup.csv")

window_order = ["Next 90 days", "91-180 days", "180+ days"]
band_order = ["Critical", "At Risk", "Neutral", "Healthy"]
band_colors = {"Critical": "#D64545", "At Risk": "#E8A33D",
               "Neutral": "#8FA6C2", "Healthy": "#3E8E5A"}

fig = plt.figure(figsize=(14, 9))
fig.suptitle("Renewal Risk & Forecast Rollup", fontsize=18, fontweight="bold", y=0.98)
gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.28)

# --- 1. ARR up for renewal vs at risk, by window ---
ax1 = fig.add_subplot(gs[0, 0])
rollup = df.groupby("renewal_window").agg(
    total_arr=("arr", "sum"), arr_at_risk=("arr_at_risk", "sum")
).reindex(window_order) / 1000
x = range(len(window_order))
w = 0.35
ax1.bar([i - w/2 for i in x], rollup["total_arr"], width=w, label="Total ARR", color="#8FA6C2")
ax1.bar([i + w/2 for i in x], rollup["arr_at_risk"], width=w, label="ARR at Risk", color="#D64545")
ax1.set_xticks(list(x))
ax1.set_xticklabels(window_order)
ax1.set_ylabel("ARR ($K)")
ax1.set_title("Total ARR vs. Risk-Weighted ARR by Window", fontsize=13, fontweight="bold")
ax1.legend(fontsize=9, frameon=False)

# --- 2. ARR at risk by CSM (next 90 days) ---
ax2 = fig.add_subplot(gs[0, 1])
next90 = df[df["renewal_window"] == "Next 90 days"]
by_csm = next90.groupby("csm")["arr_at_risk"].sum().sort_values(ascending=True) / 1000
bars2 = ax2.barh(by_csm.index, by_csm.values, color="#E8A33D")
ax2.set_title("Next-90-Day ARR at Risk by CSM", fontsize=13, fontweight="bold")
ax2.set_xlabel("ARR at risk ($K)")
for bar, val in zip(bars2, by_csm.values):
    ax2.text(val + max(by_csm)*0.02, bar.get_y() + bar.get_height()/2,
              f"${val:,.0f}K", va="center", fontsize=9)

# --- 3. Account count by health band, next 90 days ---
ax3 = fig.add_subplot(gs[1, 0])
band_counts = next90["health_band"].value_counts().reindex(band_order)
bars3 = ax3.bar(band_counts.index, band_counts.values,
                 color=[band_colors[b] for b in band_order])
ax3.set_title("Next-90-Day Renewals by Health Band", fontsize=13, fontweight="bold")
ax3.set_ylabel("Number of accounts")
for bar, val in zip(bars3, band_counts.values):
    if pd.notna(val):
        ax3.text(bar.get_x() + bar.get_width()/2, val + 0.5, str(int(val)), ha="center", fontsize=10)

# --- 4. Segment breakdown of at-risk ARR, next 90 days ---
ax4 = fig.add_subplot(gs[1, 1])
seg_risk = next90.groupby("segment")["arr_at_risk"].sum().sort_values(ascending=False) / 1000
colors_seg = ["#2E5A9C", "#8FA6C2", "#C7D3E3"][:len(seg_risk)]
ax4.pie(seg_risk.values, labels=seg_risk.index, autopct="%1.0f%%",
        colors=colors_seg, startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5})
ax4.set_title("Next-90-Day ARR at Risk by Segment", fontsize=13, fontweight="bold")

plt.savefig("renewal_risk_dashboard.png", dpi=150, bbox_inches="tight", facecolor="white")
print("Saved renewal_risk_dashboard.png")
