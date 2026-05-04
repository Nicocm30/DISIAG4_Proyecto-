from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd

AGENT_TO_ROLE: Dict[str, str] = {
    "Jett": "Duelist", "Raze": "Duelist", "Reyna": "Duelist",
    "Phoenix": "Duelist", "Yoru": "Duelist", "Neon": "Duelist",
    "Iso": "Duelist", "Waylay": "Duelist",

    "Brimstone": "Controller", "Omen": "Controller",
    "Viper": "Controller", "Astra": "Controller", "Harbor": "Controller",
    "Clove": "Controller",

    "Sage": "Sentinel", "Cypher": "Sentinel",
    "Killjoy": "Sentinel", "Chamber": "Sentinel",
    "Deadlock": "Sentinel", "Vyse": "Sentinel",

    "Sova": "Initiator", "Breach": "Initiator",
    "Skye": "Initiator", "Kayo": "Initiator", "Kay/O": "Initiator",
    "Fade": "Initiator", "Gekko": "Initiator", "Tejo": "Initiator",
}

NUMERIC_FEATURES = [
    "Average Combat Score",
    "Average Damage Per Round",
    "Kills Per Round",
    "Assists Per Round",
    "First Kills Per Round",
    "First Deaths Per Round",
    "Headshot %",
    "Clutch Success %",
    "Clutch_Success_Ratio",
    "Clutches_Won",
    "KDR",
]

CATEGORICAL_FEATURES = ["Agents", "Role"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES

CRITICAL_COLUMNS = [
    "Player",
    "Agents",
    "Average Combat Score",
    "Kills Per Round",
    "Kills:Deaths",
]


def _to_percentage(series: pd.Series) -> pd.Series:
    """Convert values such as '24%' or 24 into a numeric 0-1 percentage."""
    cleaned = pd.to_numeric(
        series.astype(str).str.replace("%", "", regex=False).str.strip(),
        errors="coerce",
    )
    return cleaned / 100.0


def _normalize_agent(value: object) -> str:
    """Take the first listed agent and normalize capitalization."""
    agent = str(value).split(",")[0].strip()
    # Preserve KAY/O as a known special case, otherwise use title case.
    if agent.upper().replace(" ", "") in {"KAY/O", "KAYO"}:
        return "Kayo"
    return agent.title()


def prepare_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Replicate the notebook preprocessing in a reusable production function."""
    df = raw_df.copy()
    existing_critical = [col for col in CRITICAL_COLUMNS if col in df.columns]
    df = df.dropna(subset=existing_critical).drop_duplicates().copy()

    # Percent columns.
    if "Headshot %" in df.columns:
        df["Headshot %"] = _to_percentage(df["Headshot %"])
    if "Clutch Success %" in df.columns:
        df["Clutch Success %"] = _to_percentage(df["Clutch Success %"])

    # KDR.
    if "Kills:Deaths" in df.columns:
        df.rename(columns={"Kills:Deaths": "KDR"}, inplace=True)
    df["KDR"] = pd.to_numeric(df["KDR"], errors="coerce")

    # Clutches (won/played) -> Clutches_Won, Clutches_Played, ratio.
    if "Clutches (won/played)" in df.columns:
        clutch_split = df["Clutches (won/played)"].astype(str).str.split("/", expand=True)
        df["Clutches_Won"] = pd.to_numeric(clutch_split[0], errors="coerce")
        df["Clutches_Played"] = pd.to_numeric(clutch_split[1], errors="coerce")
    else:
        df["Clutches_Won"] = pd.to_numeric(df.get("Clutches_Won", 0), errors="coerce")
        df["Clutches_Played"] = pd.to_numeric(df.get("Clutches_Played", 0), errors="coerce")

    df["Clutch_Success_Ratio"] = np.where(
        df["Clutches_Played"] > 0,
        df["Clutches_Won"] / df["Clutches_Played"],
        0,
    )

    # Numeric conversion for model columns.
    for col in NUMERIC_FEATURES:
        if col not in df.columns:
            df[col] = np.nan
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Agent -> Role.
    df["Agents"] = df["Agents"].apply(_normalize_agent)
    df["Role"] = df["Agents"].map(AGENT_TO_ROLE)
    df = df.dropna(subset=["Role"]).copy()

    # Feature engineering from the notebook.
    df["Offensive_Index"] = df["Kills Per Round"] + df["First Kills Per Round"]
    df["Survival_Index"] = 1 - df["First Deaths Per Round"]
    df["Clutch_Index"] = df["Clutch_Success_Ratio"] * df["Clutches_Won"]

    df["role_score_raw"] = df.apply(compute_role_score, axis=1)
    return df


def compute_role_score(row: pd.Series) -> float:
    role = row["Role"]
    adr = row["Average Damage Per Round"]
    kpr = row["Kills Per Round"]
    apr = row["Assists Per Round"]
    fkpr = row["First Kills Per Round"]
    fdpr = row["First Deaths Per Round"]
    clutch = row["Clutch_Success_Ratio"]

    if role == "Duelist":
        return 0.4 * fkpr + 0.3 * kpr - 0.2 * fdpr + 0.1 * adr
    if role == "Controller":
        return 0.35 * apr + 0.25 * adr + 0.2 * kpr - 0.2 * fdpr
    if role == "Sentinel":
        return 0.4 * clutch + 0.35 * (1 - fdpr) + 0.25 * apr
    if role == "Initiator":
        return 0.35 * apr + 0.3 * kpr + 0.2 * adr + 0.15 * fkpr
    return np.nan
