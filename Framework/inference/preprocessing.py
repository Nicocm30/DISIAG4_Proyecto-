from __future__ import annotations

from typing import Dict
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
FEATURE_COLUMNS = NUMERIC_FEATURES + ["Agents", "Role"]


def _normalize_agent(value: object) -> str:
    agent = str(value).split(",")[0].strip()
    if agent.upper().replace(" ", "") in {"KAY/O", "KAYO"}:
        return "Kayo"
    return agent.title()


def _to_percentage(value: object) -> float:
    if value is None:
        return np.nan
    raw = str(value).strip().replace("%", "")
    try:
        numeric = float(raw)
    except ValueError:
        return np.nan
    # Accept both 27.5 and 0.275. If > 1, assume human percentage.
    return numeric / 100.0 if numeric > 1 else numeric


def _parse_clutches(value: object) -> tuple[float, float, float]:
    if value is None:
        return np.nan, np.nan, np.nan
    parts = str(value).split("/")
    if len(parts) != 2:
        return np.nan, np.nan, np.nan
    try:
        won = float(parts[0])
        played = float(parts[1])
    except ValueError:
        return np.nan, np.nan, np.nan
    ratio = won / played if played > 0 else 0.0
    return won, played, ratio


def prepare_payload(payload: dict) -> pd.DataFrame:
    data = dict(payload)

    if "Kills:Deaths" in data and "KDR" not in data:
        data["KDR"] = data["Kills:Deaths"]

    if "Clutches (won/played)" in data:
        won, played, ratio = _parse_clutches(data["Clutches (won/played)"])
        data.setdefault("Clutches_Won", won)
        data.setdefault("Clutches_Played", played)
        data.setdefault("Clutch_Success_Ratio", ratio)

    if "Clutch Success %" not in data:
        data["Clutch Success %"] = data.get("Clutch_Success_Ratio", np.nan)

    data["Headshot %"] = _to_percentage(data.get("Headshot %"))
    data["Clutch Success %"] = _to_percentage(data.get("Clutch Success %"))

    agent = _normalize_agent(data.get("Agents", ""))
    role = data.get("Role") or AGENT_TO_ROLE.get(agent)
    if role is None:
        raise ValueError(f"No se puede inferir el rol para el agente: {agent}")

    data["Agents"] = agent
    data["Role"] = str(role).strip().title()

    for col in NUMERIC_FEATURES:
        data[col] = pd.to_numeric(pd.Series([data.get(col, np.nan)]), errors="coerce").iloc[0]

    return pd.DataFrame([{col: data.get(col, np.nan) for col in FEATURE_COLUMNS}])
