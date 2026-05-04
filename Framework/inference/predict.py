from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib

from preprocessing import prepare_payload

MODEL_DIR = Path("models")


def load_artifacts():
    required = [
        "role_model.pkl",
        "imputer.pkl",
        "agent_encoder.pkl",
        "role_encoder.pkl",
        "feature_columns.pkl",
    ]
    missing = [name for name in required if not (MODEL_DIR / name).exists()]
    if missing:
        raise FileNotFoundError(
            "Faltan artefactos del modelo. Ejecuta primero el contenedor de entrenamiento. "
            f"Archivos faltantes: {missing}"
        )

    return {
        "model": joblib.load(MODEL_DIR / "role_model.pkl"),
        "imputer": joblib.load(MODEL_DIR / "imputer.pkl"),
        "agent_encoder": joblib.load(MODEL_DIR / "agent_encoder.pkl"),
        "role_encoder": joblib.load(MODEL_DIR / "role_encoder.pkl"),
        "feature_columns": joblib.load(MODEL_DIR / "feature_columns.pkl"),
    }


def main() -> None:
    payload = json.loads(sys.stdin.read())
    artifacts = load_artifacts()

    df = prepare_payload(payload)
    role_name = df.loc[0, "Role"]
    agent_name = df.loc[0, "Agents"]

    # Validate categorical values against training encoders.
    if agent_name not in artifacts["agent_encoder"].classes_:
        raise ValueError(f"Agente no visto durante entrenamiento: {agent_name}")
    if role_name not in artifacts["role_encoder"].classes_:
        raise ValueError(f"Rol no visto durante entrenamiento: {role_name}")

    df["Agents"] = artifacts["agent_encoder"].transform(df["Agents"].astype(str))
    df["Role"] = artifacts["role_encoder"].transform(df["Role"].astype(str))

    X = df[artifacts["feature_columns"]]
    X_imputed = artifacts["imputer"].transform(X)
    prediction = float(artifacts["model"].predict(X_imputed)[0])
    prediction = max(0.0, min(1.0, prediction))

    print(json.dumps({
        "system": "VRCE",
        "agent": agent_name,
        "role": role_name,
        "role_compliance_probability": round(prediction, 4)
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
