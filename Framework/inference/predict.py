import sys
import json
import joblib
import numpy as np
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

MODEL_NAME = "XGBoost"
MODEL_DIR = Path("models") / MODEL_NAME


# ============================================================
# LOAD ARTIFACTS
# ============================================================

model = joblib.load(MODEL_DIR / "model.pkl")
agent_encoder = joblib.load(MODEL_DIR / "agent_encoder.pkl")
role_encoder = joblib.load(MODEL_DIR / "role_encoder.pkl")

selected_features_path = MODEL_DIR / "selected_features.json"

with open(selected_features_path, "r", encoding="utf-8") as f:
    selected_features = json.load(f)


# ============================================================
# READ INPUT
# ============================================================

try:
    input_json = json.loads(sys.stdin.read())
except Exception as e:
    print(json.dumps({
        "error": "Invalid JSON input",
        "details": str(e)
    }))
    sys.exit(1)


# ============================================================
# VALIDATION
# ============================================================

def validate_input(data):
    required_base_fields = [
        "Agents",
        "Role"
    ]

    for field in required_base_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    for feature in selected_features:
        if feature not in data:
            raise ValueError(f"Missing required feature: {feature}")


# ============================================================
# PREPARE DATA
# ============================================================

def prepare_input(data):
    data = data.copy()

    try:
        data["Agents"] = agent_encoder.transform([data["Agents"]])[0]
    except Exception:
        raise ValueError(f"Unknown agent: {data.get('Agents')}")

    try:
        data["Role"] = role_encoder.transform([data["Role"]])[0]
    except Exception:
        raise ValueError(f"Unknown role: {data.get('Role')}")

    row = []

    for feature in selected_features:
        try:
            row.append(float(data[feature]))
        except Exception:
            raise ValueError(f"Invalid numeric value for feature: {feature}")

    return np.array(row).reshape(1, -1)


# ============================================================
# PREDICT
# ============================================================

try:
    validate_input(input_json)
    X = prepare_input(input_json)

    prediction = float(model.predict(X)[0])

    prediction = max(0.0, min(1.0, prediction))

    output = {
        "model": MODEL_NAME,
        "role": input_json["Role"],
        "agent": input_json["Agents"],
        "role_probability": round(prediction, 4)
    }

    print(json.dumps(output))

except Exception as e:
    print(json.dumps({
        "error": "Prediction failed",
        "details": str(e)
    }))
    sys.exit(1)
