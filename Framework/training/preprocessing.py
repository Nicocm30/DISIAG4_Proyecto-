import pandas as pd
import numpy as np
from typing import Dict


# ============================================================
# MAPEO AGENTE -> ROL
# ============================================================

AGENT_ROLE_MAP: Dict[str, str] = {

    # Duelists
    "Jett": "Duelist",
    "Raze": "Duelist",
    "Reyna": "Duelist",
    "Phoenix": "Duelist",
    "Yoru": "Duelist",
    "Neon": "Duelist",
    "Iso": "Duelist",
    "Waylay": "Duelist",

    # Controllers
    "Omen": "Controller",
    "Brimstone": "Controller",
    "Viper": "Controller",
    "Astra": "Controller",
    "Harbor": "Controller",
    "Clove": "Controller",

    # Sentinels
    "Killjoy": "Sentinel",
    "Cypher": "Sentinel",
    "Sage": "Sentinel",
    "Chamber": "Sentinel",
    "Deadlock": "Sentinel",
    "Vyse": "Sentinel",

    # Initiators
    "Sova": "Initiator",
    "Breach": "Initiator",
    "Skye": "Initiator",
    "Kayo": "Initiator",
    "Kay/O": "Initiator",
    "Fade": "Initiator",
    "Gekko": "Initiator",
    "Tejo": "Initiator",
}


# ============================================================
# LIMPIEZA PORCENTAJES
# ============================================================

def clean_percentage(value):

    if pd.isna(value):
        return np.nan

    if isinstance(value, str):
        return float(value.replace("%", "").strip())

    return value


# ============================================================
# CLUTCHES
# ============================================================

def extract_clutches_won(value):

    if pd.isna(value):
        return 0

    try:
        return int(str(value).split("/")[0])

    except:
        return 0


def extract_clutches_played(value):

    if pd.isna(value):
        return 0

    try:
        return int(str(value).split("/")[1])

    except:
        return 0

# ============================================================
# NORMALIZE AGENT
# ============================================================

def _normalize_agent(value: object) -> str:
    """Take the first listed agent and normalize capitalization."""
    agent = str(value).split(",")[0].strip()
    # Preserve KAY/O as a known special case, otherwise use title case.
    if agent.upper().replace(" ", "") in {"KAY/O", "KAYO"}:
        return "Kayo"
    return agent.title()

# ============================================================
# AGENT -> ROLE
# ============================================================

def map_agent_to_role(agent):

    if pd.isna(agent):
        return "Unknown"

    first_agent = str(agent).split(",")[0].strip()

    return AGENT_ROLE_MAP.get(first_agent, "Unknown")


# ============================================================
# ROLE SCORE
# ============================================================

def calculate_role_score(row, adr_max):

    role = row["Role"]

    if role == "Duelist":

        return (
            0.40 * row["First Kills Per Round"] +
            0.30 * row["Kills Per Round"] -
            0.20 * row["First Deaths Per Round"] +
            0.10 * (row["Average Damage Per Round"] / adr_max)
        )

    elif role == "Controller":

        return (
            0.35 * row["Assists Per Round"] +
            0.25 * (row["Average Damage Per Round"] / adr_max) +
            0.20 * row["Kills Per Round"] -
            0.20 * row["First Deaths Per Round"]
        )

    elif role == "Sentinel":

        return (
            0.30 * row["Clutch_Success_Ratio"] +
            0.25 * (1 - row["First Deaths Per Round"]) +
            0.25 * (1 / (row["Deaths"] + 1)) +
            0.20 * row["Assists Per Round"]
        )

    elif role == "Initiator":

        return (
            0.35 * row["Assists Per Round"] +
            0.30 * row["Kills Per Round"] +
            0.20 * (row["Average Damage Per Round"] / adr_max) +
            0.15 * row["First Kills Per Round"]
        )

    return np.nan


# ============================================================
# PIPELINE
# ============================================================

def preprocess_dataset(df):

    # ----------------------------------------
    # LIMPIEZA PORCENTAJES
    # ----------------------------------------

    percentage_columns = [
        "Kill, Assist, Trade, Survive %",
        "Headshot %",
        "Clutch Success %"
    ]

    for col in percentage_columns:

        if col in df.columns:
            df[col] = df[col].apply(clean_percentage)

    # ----------------------------------------
    # CLUTCHES
    # ----------------------------------------

    df["Clutches_Won"] = df["Clutches (won/played)"].apply(
        extract_clutches_won
    )

    df["Clutches_Played"] = df["Clutches (won/played)"].apply(
        extract_clutches_played
    )

    df["Clutch_Success_Ratio"] = np.where(
        df["Clutches_Played"] > 0,
        df["Clutches_Won"] / df["Clutches_Played"],
        0
    )

    # ----------------------------------------
    # KDR
    # ----------------------------------------

    df["KDR"] = np.where(
        df["Deaths"] > 0,
        df["Kills"] / df["Deaths"],
        df["Kills"]
    )

    # ----------------------------------------
    # ROLE
    # ----------------------------------------
    df["Agents"] = df["Agents"].apply(_normalize_agent)

    df["Role"] = df["Agents"].apply(map_agent_to_role)

    df = df[df["Role"] != "Unknown"].copy()

    # ----------------------------------------
    # ROLE SCORE
    # ----------------------------------------

    adr_max = df["Average Damage Per Round"].max()

    df["role_score_raw"] = df.apply(
        lambda row: calculate_role_score(row, adr_max),
        axis=1
    )

    return df
