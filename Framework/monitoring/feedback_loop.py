import json
import subprocess
from pathlib import Path


DRIFT_RESULTS_PATH = Path("/app/monitoring/reports/drift_results.json")
DRIFT_THRESHOLD = 1


def load_drift_results():
    if not DRIFT_RESULTS_PATH.exists():
        raise FileNotFoundError(f"No existe {DRIFT_RESULTS_PATH}")

    with open(DRIFT_RESULTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def should_retrain(results):
    drifted_features = [
        result for result in results
        if result.get("drift_detected") is True
    ]

    return len(drifted_features) >= DRIFT_THRESHOLD, drifted_features


def main():
    results = load_drift_results()

    retrain_required, drifted_features = should_retrain(results)

    print("\n===== FEEDBACK LOOP =====\n")

    if retrain_required:
        print("Drift detectado.")
        print("Variables con drift:")

        for item in drifted_features:
            print(f"- {item['feature']} | p-value={item['p_value']:.6f}")

        print("\nReentrenamiento recomendado.")
        print("Ejecuta:")
        print("docker compose run --rm training")

    else:
        print("No se detectó drift suficiente.")
        print("No se recomienda reentrenamiento.")


if __name__ == "__main__":
    main()
