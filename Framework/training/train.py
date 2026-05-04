from __future__ import annotations

from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from xgboost import XGBRegressor

from preprocessing import FEATURE_COLUMNS, CATEGORICAL_FEATURES, prepare_dataframe, AGENT_TO_ROLE

DATA_PATH = Path("data/players_stats.csv")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"No se encontró el dataset en {DATA_PATH.resolve()}")

    raw_df = pd.read_csv(DATA_PATH)
    df = prepare_dataframe(raw_df)

    # Drop rows without a valid target.
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=["role_score_raw"]).copy()

    score_scaler = MinMaxScaler()
    df["role_score"] = score_scaler.fit_transform(df[["role_score_raw"]]).ravel()

    # Preserve clean dataset for documentation/debugging.
    df.to_csv(MODEL_DIR / "dataset_players_processed.csv", index=False)

    model_df = df[FEATURE_COLUMNS + ["role_score"]].copy()

    agent_encoder = LabelEncoder()
    role_encoder = LabelEncoder()
    model_df["Agents"] = agent_encoder.fit_transform(model_df["Agents"].astype(str))
    model_df["Role"] = role_encoder.fit_transform(model_df["Role"].astype(str))

    X = model_df[FEATURE_COLUMNS]
    y = model_df["role_score"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # XGBoost tolerates missing values, but an imputer makes inference stable and explicit.
    imputer = SimpleImputer(strategy="median")
    X_train_imputed = imputer.fit_transform(X_train)
    X_test_imputed = imputer.transform(X_test)

    model = XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        objective="reg:squarederror",
        tree_method="hist",
        random_state=42,
        n_jobs=1,
    )
    model.fit(X_train_imputed, y_train)

    predictions = model.predict(X_test_imputed)
    rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
    mae = float(mean_absolute_error(y_test, predictions))
    r2 = float(r2_score(y_test, predictions))

    metrics = {
        "rows_raw": int(len(raw_df)),
        "rows_processed": int(len(df)),
        "features": FEATURE_COLUMNS,
        "target": "role_score",
        "model": "XGBRegressor",
        "test_size": 0.2,
        "random_state": 42,
        "rmse": rmse,
        "mae": mae,
        "r2": r2,
    }

    joblib.dump(model, MODEL_DIR / "role_model.pkl")
    joblib.dump(imputer, MODEL_DIR / "imputer.pkl")
    joblib.dump(agent_encoder, MODEL_DIR / "agent_encoder.pkl")
    joblib.dump(role_encoder, MODEL_DIR / "role_encoder.pkl")
    joblib.dump(score_scaler, MODEL_DIR / "score_scaler.pkl")
    joblib.dump(FEATURE_COLUMNS, MODEL_DIR / "feature_columns.pkl")
    joblib.dump(AGENT_TO_ROLE, MODEL_DIR / "agent_to_role.pkl")

    with open(MODEL_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print("Modelo entrenado correctamente.")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
