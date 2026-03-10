import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

data_dir = r"C:\Users\eclow\Documents\GitHub\cab-persistency\updated_2025\clean-data"
file_name = "regime_counts.xlsx"
path = os.path.join(data_dir, file_name)

df = pd.read_excel(path)

df["year"] = pd.to_numeric(df["year"], errors="coerce")
df = df.dropna(subset=["year"]).copy()
df["date"] = pd.to_datetime(df["year"].astype(int).astype(str) + "-01-01")
df = df.sort_values("date").set_index("date")

cols   = ["Pct. Stationary", "Pct. Unit Root", "Pct. Explosive"]
labels = ["Stationary", "Unit Root", "Explosive"]

df[cols] = df[cols].apply(pd.to_numeric, errors="coerce").clip(lower=0)
df[cols] = df[cols].div(df[cols].sum(axis=1), axis=0)

COLORS = {
    "Stationary": "#f4a582",
    "Unit Root":  "#92a8d1",
    "Explosive":  "#7fcdbb",
}

fig, ax = plt.subplots(figsize=(10, 4))
width_days = 300

bottom = np.zeros(len(df))
for c, lab in zip(cols, labels):
    ax.bar(
        df.index,
        df[c].to_numpy(),
        bottom=bottom,
        width=width_days,
        label=lab,
        color=COLORS[lab],
        edgecolor="white",
        linewidth=0.6,
        alpha=0.95
    )
    bottom += df[c].to_numpy()

ax.xaxis.set_major_locator(mdates.YearLocator(base=5))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
fig.autofmt_xdate()

ax.set_ylim(0, 1)
ax.set_ylabel("Share")

ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, -0.18),
    ncol=3,
    frameon=False
)

plt.tight_layout()

out_dir = os.path.join(
    r"C:\Users\eclow\Documents\GitHub\cab-persistency\updated_2025",
    r"results\data-summaries\plots\data-summaries-ii"
)
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "annual_regime_count.jpg")

fig.savefig(out_path, dpi=300, bbox_inches="tight")
plt.show()

print(f"Saved to: {out_path}")
