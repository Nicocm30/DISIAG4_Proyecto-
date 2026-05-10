import os
import json
import joblib
import mlflow
import pandas as pd

from pathlib import Path

from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split

from preprocessing import preprocess_dataset
from feature_selection import select_best_features
from train import train_knn, train_xgboost, evaluate_model


# ============================================================
# CONFIG
# ============================================================

DATA_DIR = Path("/app/data")
DATA_PATTERN = "players_stats_*.csv"
MODELS_DIR = Path("/app/models")

MODELS_DIR.mkdir(parents=True, exist_ok=True)

MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://mlflow:5000"
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("VRCE Role Compliance")


FEATURE_COLUMNS = [
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
    "Agents",
    "Role",
    "Dataset_Year"
]

TARGET_COLUMN = "role_score"


# ============================================================
# UTILS
# ============================================================

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def log_model_run(
    model_name,
    model,
    best_params,
    metrics,
    selected_features,
    artifacts_dir,
    y_test,
    y_pred
):
    if mlflow.active_run() is not None:
        mlflow.end_run()

    with mlflow.start_run(run_name=model_name):

        mlflow.set_tag("project", "VRCE")
        mlflow.set_tag("problem_type", "regression")
        mlflow.set_tag("target", TARGET_COLUMN)
        mlflow.set_tag("feature_selection", "SelectKBest")
        mlflow.set_tag("model_name", model_name)

        mlflow.log_param("dataset_name", "players_stats.csv")
        mlflow.log_param("dataset_years", "2023,2024,2025")
        mlflow.log_param("dataset_mode", "multi_year")
        mlflow.log_param("num_selected_features", len(selected_features))
        mlflow.log_param("selected_features", selected_features)

        for param_name, param_value in best_params.items():
            mlflow.log_param(param_name, param_value)

        mlflow.log_metric("rmse", metrics["rmse"])
        mlflow.log_metric("mae", metrics["mae"])
        mlflow.log_metric("r2", metrics["r2"])

        predictions_df = pd.DataFrame({
            "real": y_test.values,
            "predicted": y_pred
        })

        predictions_df["absolute_error"] = (
            predictions_df["real"] - predictions_df["predicted"]
        ).abs()

        predictions_path = artifacts_dir / "predictions.csv"
        predictions_df.to_csv(predictions_path, index=False)

        metrics_path = artifacts_dir / "metrics.json"
        save_json(metrics, metrics_path)

        params_path = artifacts_dir / "best_params.json"
        save_json(best_params, params_path)

        selected_features_path = artifacts_dir / "selected_features.json"
        save_json(selected_features, selected_features_path)

        model_path = artifacts_dir / "model.pkl"
        joblib.dump(model, model_path)

        mlflow.log_artifacts(str(artifacts_dir), artifact_path=model_name)


def load_datasets():
    csv_files = sorted(DATA_DIR.glob(DATA_PATTERN))

    if not csv_files:
        raise FileNotFoundError(
            f"No se encontraron archivos con patrón {DATA_PATTERN} en {DATA_DIR}"
        )

    dfs = []

    for file_path in csv_files:
        temp_df = pd.read_csv(file_path)

        # Extrae el año desde nombres tipo players_stats_2023.csv
        year = file_path.stem.split("_")[-1]

        try:
            temp_df["Dataset_Year"] = int(year)
        except ValueError:
            temp_df["Dataset_Year"] = 0

        temp_df["Dataset_File"] = file_path.name

        dfs.append(temp_df)

    df = pd.concat(dfs, ignore_index=True)

    return df, csv_files


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    print("Loading dataset...")
    print("Loading datasets...")
    df, csv_files = load_datasets()

    dataset_info = {
        "dataset_files": [file.name for file in csv_files],
        "dataset_years": sorted(df["Dataset_Year"].unique().tolist()),
        "original_rows": int(df.shape[0]),
        "original_columns": int(df.shape[1]),
        "columns": df.columns.tolist()
    }

    print("Preprocessing dataset...")
    df = preprocess_dataset(df)

    score_scaler = MinMaxScaler()

    df[TARGET_COLUMN] = score_scaler.fit_transform(
        df[["role_score_raw"]]
    )

    df_model = df[FEATURE_COLUMNS + [TARGET_COLUMN]].dropna().copy()

    dataset_info.update({
        "processed_rows": int(df_model.shape[0]),
        "processed_columns": int(df_model.shape[1])
    })

    print("Encoding categorical variables...")
    agent_encoder = LabelEncoder()
    role_encoder = LabelEncoder()

    df_model["Agents"] = agent_encoder.fit_transform(
        df_model["Agents"].astype(str)
    )

    df_model["Role"] = role_encoder.fit_transform(
        df_model["Role"].astype(str)
    )

    X = df_model[FEATURE_COLUMNS]
    y = df_model[TARGET_COLUMN]

    print("Selecting features with SelectKBest...")
    selected_features = select_best_features(X, y, k=10)

    X = X[selected_features]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    dataset_info.update({
        "train_rows": int(X_train.shape[0]),
        "test_rows": int(X_test.shape[0]),
        "target": TARGET_COLUMN
    })

    # Shared artifacts
    shared_dir = MODELS_DIR / "shared"
    shared_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(agent_encoder, shared_dir / "agent_encoder.pkl")
    joblib.dump(role_encoder, shared_dir / "role_encoder.pkl")
    joblib.dump(score_scaler, shared_dir / "score_scaler.pkl")
    save_json(dataset_info, shared_dir / "dataset_info.json")

    # ==========================
    # KNN
    # ==========================

    print("Training KNN Regressor...")

    knn_dir = MODELS_DIR / "KNN"
    knn_dir.mkdir(parents=True, exist_ok=True)

    knn_model, knn_params = train_knn(X_train, y_train)
    knn_metrics, knn_pred = evaluate_model(knn_model, X_test, y_test)

    save_json(dataset_info, knn_dir / "dataset_info.json")
    joblib.dump(agent_encoder, knn_dir / "agent_encoder.pkl")
    joblib.dump(role_encoder, knn_dir / "role_encoder.pkl")
    joblib.dump(score_scaler, knn_dir / "score_scaler.pkl")

    log_model_run(
        model_name="KNN",
        model=knn_model,
        best_params=knn_params,
        metrics=knn_metrics,
        selected_features=selected_features,
        artifacts_dir=knn_dir,
        y_test=y_test,
        y_pred=knn_pred
    )

    print("KNN Metrics:")
    print(knn_metrics)

    # ==========================
    # XGBoost
    # ==========================

    print("Training XGBoost Regressor...")

    xgb_dir = MODELS_DIR / "XGBoost"
    xgb_dir.mkdir(parents=True, exist_ok=True)

    xgb_model, xgb_params = train_xgboost(X_train, y_train)
    xgb_metrics, xgb_pred = evaluate_model(xgb_model, X_test, y_test)

    save_json(dataset_info, xgb_dir / "dataset_info.json")
    joblib.dump(agent_encoder, xgb_dir / "agent_encoder.pkl")
    joblib.dump(role_encoder, xgb_dir / "role_encoder.pkl")
    joblib.dump(score_scaler, xgb_dir / "score_scaler.pkl")

    if hasattr(xgb_model, "feature_importances_"):
        feature_importance_df = pd.DataFrame({
            "feature": selected_features,
            "importance": xgb_model.feature_importances_
        }).sort_values(by="importance", ascending=False)

        feature_importance_df.to_csv(
            xgb_dir / "feature_importance.csv",
            index=False
        )

    log_model_run(
        model_name="XGBoost",
        model=xgb_model,
        best_params=xgb_params,
        metrics=xgb_metrics,
        selected_features=selected_features,
        artifacts_dir=xgb_dir,
        y_test=y_test,
        y_pred=xgb_pred
    )

    print("XGBoost Metrics:")
    print(xgb_metrics)

    # ==========================
    # Comparison
    # ==========================

    comparison_df = pd.DataFrame([
        {
            "model": "KNN",
            **knn_metrics
        },
        {
            "model": "XGBoost",
            **xgb_metrics
        }
    ])

    comparison_path = MODELS_DIR / "model_comparison.csv"
    comparison_df.to_csv(comparison_path, index=False)

    print("Model comparison:")
    print(comparison_df)

    print("Training pipeline completed.")


if __name__ == "__main__":
    main()
