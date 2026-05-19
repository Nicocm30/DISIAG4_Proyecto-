import sys
import json
import joblib
import numpy as np
from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIG
# ============================================================

CHAMPION_MODEL_NAME = "XGBoost"
CHALLENGER_MODEL_NAME = "KNN"

MODELS_DIR = Path("models")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

SHADOW_LOG_PATH = LOG_DIR / "shadow_testing.jsonl"


# ============================================================
# LOAD MODEL BUNDLE
# ============================================================

def load_model_bundle(model_name):
    model_dir = MODELS_DIR / model_name

    if not model_dir.exists():
        raise FileNotFoundError(f"Model directory not found: {model_dir}")

    model = joblib.load(model_dir / "model.pkl")
    agent_encoder = joblib.load(model_dir / "agent_encoder.pkl")
    role_encoder = joblib.load(model_dir / "role_encoder.pkl")

    with open(model_dir / "selected_features.json", "r", encoding="utf-8") as f:
        selected_features = json.load(f)

    return {
        "name": model_name,
        "model": model,
        "agent_encoder": agent_encoder,
        "role_encoder": role_encoder,
        "selected_features": selected_features
    }


champion = load_model_bundle(CHAMPION_MODEL_NAME)
challenger = load_model_bundle(CHALLENGER_MODEL_NAME)


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

def validate_input(data, selected_features):
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

def prepare_input(data, bundle):
    data = data.copy()

    agent_encoder = bundle["agent_encoder"]
    role_encoder = bundle["role_encoder"]
    selected_features = bundle["selected_features"]

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
# PREDICTION
# ============================================================

def predict_with_bundle(data, bundle):
    validate_input(data, bundle["selected_features"])
    X = prepare_input(data, bundle)

    prediction = float(bundle["model"].predict(X)[0])
    prediction = max(0.0, min(1.0, prediction))

    return prediction


# ============================================================
# SHADOW LOGGING
# ============================================================

def log_shadow_result(data, champion_prediction, challenger_prediction):
    delta = abs(champion_prediction - challenger_prediction)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": data.get("Agents"),
        "role": data.get("Role"),
        "champion_model": CHAMPION_MODEL_NAME,
        "champion_prediction": round(champion_prediction, 6),
        "challenger_model": CHALLENGER_MODEL_NAME,
        "challenger_prediction": round(challenger_prediction, 6),
        "prediction_delta": round(delta, 6)
    }

    with open(SHADOW_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


# ============================================================
# MAIN
# ============================================================

try:
    champion_prediction = predict_with_bundle(input_json, champion)

    try:
        challenger_prediction = predict_with_bundle(input_json, challenger)
        log_shadow_result(
            input_json,
            champion_prediction,
            challenger_prediction
        )
    except Exception as shadow_error:
        with open(SHADOW_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "agent": input_json.get("Agents"),
                "role": input_json.get("Role"),
                "champion_model": CHAMPION_MODEL_NAME,
                "challenger_model": CHALLENGER_MODEL_NAME,
                "shadow_error": str(shadow_error)
            }) + "\n")

    output = {
        "model": CHAMPION_MODEL_NAME,
        "role": input_json["Role"],
        "agent": input_json["Agents"],
        "role_probability": round(champion_prediction, 4)
    }

    print(json.dumps(output))

except Exception as e:
    print(json.dumps({
        "error": "Prediction failed",
        "details": str(e)
    }))
    sys.exit(1)
