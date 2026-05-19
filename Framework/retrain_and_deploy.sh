#!/bin/bash

echo "=== VRCE Retraining + Deployment ==="

echo "1. Ejecutando análisis de drift..."
docker compose run --rm training python //app/monitoring/drift_report.py

echo "2. Evaluando feedback loop..."
docker compose run --rm training python //app/monitoring/feedback_loop.py

echo "3. Alertas..."
docker compose run --rm training python /app/monitoring/evidently/alerting.py

DRIFT_FILE="monitoring/reports/drift_results.json"

if grep -q '"drift_detected": true' "$DRIFT_FILE"; then
    echo "Drift detectado. Reentrenando modelos..."

    docker compose run --rm training

    echo "Reiniciando API de inferencia..."
    docker compose up -d --build inference

    echo "Despliegue actualizado correctamente."
else
    echo "No se detectó drift. No se reentrena."
fi
