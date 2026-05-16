# VRCE - Framework MLOps para Evaluación de Cumplimiento de Rol en Valorant

VRCE (Valorant Role Compliance Evaluation) es un framework de inteligencia artificial orientado a estimar la probabilidad de cumplimiento del rol de un jugador profesional de Valorant mediante técnicas de Machine Learning y prácticas MLOps.

El sistema integra:

* entrenamiento y evaluación de modelos;
* despliegue mediante API REST;
* documentación Swagger;
* monitorización operativa;
* trazabilidad experimental con MLflow;
* detección de drift;
* feedback loop para reentrenamiento.

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
├── data/
│   ├── players_stats_2023.csv
│   ├── players_stats_2024.csv
│   └── players_stats_2025.csv
│
├── training/
│   ├── main.py
│   ├── train.py
│   ├── preprocessing.py
│   ├── feature_selection.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── inference/
│   ├── predict.py
│   ├── server.js
│   ├── swagger.json
│   ├── package.json
│   ├── requirements.txt
│   ├── Dockerfile
│   └── models/
│
├── monitoring/
│   ├── prometheus.yml
│   ├── reports/
│   ├── drift_report.py
│   └── feedback_loop.py
│
├── mlruns/
├── docker-compose.yml
└── README.md
```

---

# 1. Entrenamiento del modelo

Ejecutar:

```bash
docker compose run --rm training
```

El pipeline realiza:

* unión de datasets históricos (2023–2025);
* preprocessing y limpieza;
* feature engineering;
* selección de características con SelectKBest;
* entrenamiento de:

  * KNN Regressor
  * XGBoost Regressor
* evaluación mediante:

  * RMSE
  * MAE
  * R²
* registro experimental en MLflow.

---

# Artefactos generados

```text
inference/models/
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

# 4. Verificación de estado

```bash
curl http://localhost:3000/health
```

---

# 5. Predicción

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
  "role_probability": 0.8732
}
```

---

# 6. Swagger - Documentación API

Abrir:

```text
http://localhost:3000/api-docs
```

Endpoints disponibles:

* `GET /health`
* `POST /predict`
* `GET /metrics`

---

# 7. Monitorización operativa

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

# 8. Prometheus

Levantar:

```bash
docker compose up prometheus
```

Abrir:

```text
http://localhost:9090
```

Consultas ejemplo:

```promql
vrce_http_requests_total
```

```promql
vrce_prediction_latency_seconds_count
```

```promql
vrce_prediction_latency_seconds_sum
```

---

# 9. Grafana

Levantar:

```bash
docker compose up grafana
```

Abrir:

```text
http://localhost:3001
```

Credenciales iniciales:

```text
usuario: admin
contraseña: admin
```

Grafana permite:

* visualización en tiempo real;
* monitoreo operativo;
* análisis de latencia;
* seguimiento de peticiones.

---

# 10. Detección de Drift

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

# 11. Feedback Loop y Reentrenamiento

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

# 12. Capacidades MLOps del framework

VRCE incorpora capacidades MLOps orientadas a mantener la estabilidad y trazabilidad del sistema:

* monitorización operativa;
* trazabilidad experimental;
* gestión de artefactos;
* comparación de modelos;
* observabilidad;
* detección de drift;
* feedback loop;
* reentrenamiento controlado.

---

# Consideraciones técnicas

* El sistema utiliza aprendizaje supervisado con etiquetas generadas heurísticamente.
* El modelo final seleccionado corresponde a XGBoost debido a su mejor rendimiento sobre datos tabulares.
* La inclusión de múltiples años mejora la generalización.
* Puede existir drift temporal debido a cambios en el meta competitivo de Valorant.
* La variable `Dataset_Year` permite capturar variaciones temporales entre temporadas.

---
