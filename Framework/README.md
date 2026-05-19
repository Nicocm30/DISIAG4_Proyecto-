# VRCE - Framework MLOps para Evaluación de Cumplimiento de Rol en Valorant

VRCE (Valorant Role Compliance Evaluation) es un framework de inteligencia artificial orientado a estimar la probabilidad de cumplimiento del rol de un jugador profesional de Valorant mediante técnicas de Machine Learning y prácticas MLOps.

El sistema integra:

* entrenamiento y evaluación de modelos;
* despliegue mediante API REST;
* documentación Swagger;
* monitorización operativa;
* trazabilidad experimental con MLflow;
* visualización en grafana de métricas obtenida en prometheus
* detección de drift;
* feedback loop para reentrenamiento.
* automatización del ciclo MLOps

---

# Arquitectura general

El framework está compuesto por múltiples servicios desacoplados mediante contenedores Docker:

* `training`: entrenamiento y evaluación de modelos.
* `inference`: API REST para inferencia.
* `mlflow`: trazabilidad y tracking experimental.
* `prometheus`: recolección de métricas operativas.
* `grafana`: visualización y monitorización.
* `monitoring`: análisis de drift y feedback loop.

---

# Estructura del proyecto

```text
VRCE/
├── training/
│   ├── data/
├── inference/
├── monitoring/
│   ├── reports/
├── logs/
├── mlruns/
├── models/
├── .dockerignore
├── docker-compose.yml
├── README.md
└── retrain_and_deploy.sh
```

---

# 1. Entrenamiento

```bash
docker compose run --rm training
```

Modelos:

- KNN Regressor
- XGBoost Regressor

Métricas:

- RMSE
- MAE
- R²

---

# Artefactos generados

```text
models/
├── KNN/
├── XGBoost/
├── shared/
└── model_comparison.csv
```

Cada modelo almacena:

* modelo serializado;
* métricas;
* parámetros;
* predicciones;
* variables seleccionadas;
* encoders;
* información del dataset.

---

# 2. MLflow - Tracking de experimentos

Levantar MLflow:

```bash
docker compose up mlflow
```

Abrir:

```text
http://localhost:5000
```

MLflow registra:

* parámetros;
* métricas;
* datasets utilizados;
* variables seleccionadas;
* artefactos;
* comparación de modelos;
* experimentos históricos.

---

# 3. API de inferencia

Levantar:

```bash
docker compose up --build inference
```

La API utiliza el modelo XGBoost para generar predicciones.

---

## Verificación de estado

```bash
curl http://localhost:3000/health
```

---

## Predicción

```bash
curl -X POST http://localhost:3000/predict \
-H "Content-Type: application/json" \
-d '{
  "Average Combat Score": 220,
  "Average Damage Per Round": 140,
  "Kills Per Round": 0.8,
  "Assists Per Round": 0.3,
  "First Kills Per Round": 0.15,
  "First Deaths Per Round": 0.12,
  "Headshot %": 25,
  "Clutch Success %": 30,
  "Clutch_Success_Ratio": 0.3,
  "Clutches_Won": 5,
  "KDR": 1.2,
  "Agents": "Jett",
  "Role": "Duelist"
}'
```

Respuesta:

```json
{
  "model": "XGBoost",
  "role": "Duelist",
  "agent": "Jett",
  "role_probability": 0.4932
}
```

---

# 4. Swagger - Documentación API

Abrir:

```text
http://localhost:3000/api-docs
```

Endpoints disponibles:

* `GET /health`
* `POST /predict`
* `GET /metrics`

---

# 5. Monitorización operativa

## Endpoint de métricas

La API expone métricas Prometheus mediante:

```text
http://localhost:3000/metrics
```

Métricas implementadas:

* número total de requests;
* latencia de predicción;
* estado del servicio.

---

Prometheus:

http://localhost:9090

Grafana:

http://localhost:3001

Métricas:

- vrce_http_requests_total
- vrce_prediction_latency_seconds

---

# 6. Detección de Drift

El framework incorpora análisis de drift para detectar cambios en la distribución de los datos respecto al dataset de referencia.

## Variables monitorizadas

* Average Combat Score
* Average Damage Per Round
* Kills Per Round
* Assists Per Round
* First Kills Per Round
* First Deaths Per Round

## Tecnologías utilizadas

* pandas
* scipy
* matplotlib

## Método estadístico

Kolmogorov-Smirnov Test (KS Test).

---

# Generación de reporte de drift

Ejecutar:

```bash
docker compose run --rm training python /app/monitoring/evidently/drift_report.py
```

Artefactos generados:

```text
monitoring/reports/
├── drift_results.json
├── *.png
```

---

# 7. Feedback Loop y Reentrenamiento

El sistema incorpora un mecanismo básico de feedback loop orientado a la mejora continua del modelo.

Flujo:

```text
Datos actuales
↓
Detección de drift
↓
Recomendación de reentrenamiento
↓
Nuevo entrenamiento
↓
Registro en MLflow
```

Ejecutar:

```bash
docker compose run --rm training python /app/monitoring/evidently/feedback_loop.py
```

Si se detecta drift significativo, el sistema recomienda reentrenamiento.

---

# 8. Alertas

Sistema de alertas por correo:

- alerta operativa (latencia)
- alerta de modelo (drift)

```bash
docker compose run --rm training python /app/monitoring/evidently/alerting.py
```

---

# 9. Retraining automático

Script:

```bash
./retrain_and_deploy.sh
```

O servicio continuo:

```bash
docker compose up retrainer
```

---

# 10. Shadow Testing (Champion-Challenger)

Implementado en la API:

- Champion: XGBoost (respuesta real)
- Challenger: KNN (evaluación interna)

Logs:

```text
logs/shadow_testing.jsonl
```

Contenido:

- predicción champion
- predicción challenger
- diferencia (delta)

---

# Capacidades MLOps

- API productiva
- monitorización
- drift detection
- alertas automáticas
- retraining automatizado
- despliegue automático
- shadow testing
- trazabilidad completa

---

# Consideraciones

- dataset multi-año (2023–2025)
- posible drift por cambios de meta
- modelo final: XGBoost
