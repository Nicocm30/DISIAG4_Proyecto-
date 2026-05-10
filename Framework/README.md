# VRCE - Despliegue del modelo mediante API

Arquitectura basada en microservicios con contenedores Docker:

- `training`: entrena múltiples modelos (KNN y XGBoost) utilizando datasets históricos (2023, 2024, 2025) y registra experimentos con MLflow.
- `inference`: expone una API REST (NodeJS + Express) que realiza inferencia utilizando el modelo seleccionado (por defecto XGBoost).

---

## Estructura del proyecto

```
VRCE/
├── training/
│   ├── data/
│   │   ├── players_stats_2023.csv
│   │   ├── players_stats_2024.csv
│   │   └── players_stats_2025.csv
│   ├── main.py
│   ├── train.py
│   ├── preprocessing.**py**
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
├── mlruns/
├── docker-compose.yml
└── README.md
```

---

## 1. Entrenamiento del modelo

Ejecutar:

```
docker compose run --rm training
```

Esto realiza:

- unión de datasets 2023–2025
- preprocessing y feature engineering
- selección de variables (SelectKBest)
- entrenamiento de:
  - KNN Regressor
  - XGBoost Regressor
- evaluación (RMSE, MAE, R²)
- registro en MLflow

### Artefactos generados

```
inference/models/
├── KNN/
├── XGBoost/
├── shared/
└── model_comparison.csv
```

---

## 2. MLflow (Tracking de experimentos)

Levantar MLflow:

```
docker compose up mlflow
```

Abrir:

```
http://localhost:5000
```

Se registran:

- parámetros del modelo
- métricas
- features seleccionadas
- dataset utilizado
- artefactos del modelo

---

## 3. Levantar API de inferencia

```
docker compose up --build inference
```

---

## 4. Verificar API

```
curl http://localhost:3000/health
```

---

## 5. Realizar predicción

```
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

```
{
  "model": "XGBoost",
  "role": "Duelist",
  "agent": "Jett",
  "role_probability": 0.8732
}
```

---

## 6. Swagger (Documentación API)

Abrir:

```
http://localhost:3000/api-docs
```

---

## Notas técnicas

- El sistema utiliza aprendizaje supervisado con etiquetas generadas heurísticamente.
- Se emplea selección de características para reducir dimensionalidad.
- Se comparan múltiples modelos para validación experimental.
- MLflow garantiza trazabilidad completa del experimento.
- El modelo final es XGBoost por su mejor rendimiento en datos tabulares.

---

## Consideraciones

- La inclusión de múltiples años mejora la generalización.
- Puede introducir sesgo temporal por cambios en el meta del juego.
- Se incluye la variable `Dataset_Year` para capturar variaciones temporales.
