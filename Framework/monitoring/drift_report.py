import json
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from scipy.stats import ks_2samp


REFERENCE_PATH = "/app/data/players_stats_2023.csv"
CURRENT_PATH = "/app/data/players_stats_2025.csv"

OUTPUT_DIR = Path("/app/monitoring/reports")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

reference_df = pd.read_csv(REFERENCE_PATH)
current_df = pd.read_csv(CURRENT_PATH)


# ============================================================
# NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "Average Combat Score",
    "Average Damage Per Round",
    "Kills Per Round",
    "Assists Per Round",
    "First Kills Per Round",
    "First Deaths Per Round"
]


# ============================================================
# DRIFT ANALYSIS
# ============================================================

drift_results = []

for column in numeric_columns:

    ref = reference_df[column].dropna()
    cur = current_df[column].dropna()

    ks_stat, p_value = ks_2samp(ref, cur)

    drift_detected = bool(p_value < 0.05)

    result = {
        "feature": column,
        "reference_mean": float(ref.mean()),
        "current_mean": float(cur.mean()),
        "reference_std": float(ref.std()),
        "current_std": float(cur.std()),
        "ks_statistic": float(ks_stat),
        "p_value": float(p_value),
        "drift_detected": bool(drift_detected)
    }

    drift_results.append(result)

    # ==========================================
    # HISTOGRAM
    # ==========================================

    plt.figure(figsize=(8, 5))

    plt.hist(
        ref,
        bins=30,
        alpha=0.5,
        label="Reference (2023)"
    )

    plt.hist(
        cur,
        bins=30,
        alpha=0.5,
        label="Current (2025)"
    )

    plt.title(f"Drift Analysis - {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.legend()

    plot_path = OUTPUT_DIR / f"{column}_drift.png"

    plt.savefig(plot_path)
    plt.close()


# ============================================================
# SAVE JSON
# ============================================================

json_path = OUTPUT_DIR / "drift_results.json"

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(drift_results, f, indent=4)


# ============================================================
# SUMMARY
# ============================================================

print("\n===== DRIFT ANALYSIS =====\n")

for result in drift_results:

    print(f"Feature: {result['feature']}")
    print(f"P-Value: {result['p_value']:.6f}")
    print(f"Drift Detected: {result['drift_detected']}")
    print("-" * 40)

print(f"\nJSON saved at: {json_path}")
print(f"Plots saved at: {OUTPUT_DIR}")
