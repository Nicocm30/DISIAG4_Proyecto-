# VRCE - Despliegue del modelo mediante API

Arquitectura con dos contenedores:

- `training`: entrena el modelo XGBoost a partir del CSV sin procesar.
- `inference`: expone una API NodeJS/Express y ejecuta la inferencia mediante Python.

## Estructura

```text
vrce_docker/
├── training/
│   ├── data/players_stats.csv
│   ├── preprocessing.py
│   ├── train.py
│   ├── requirements.txt
│   └── Dockerfile
├── inference/
│   ├── preprocessing.py
│   ├── predict.py
│   ├── server.js
│   ├── package.json
│   ├── requirements.txt
│   └── Dockerfile
├── models/
└── docker-compose.yml
```

## 1. Entrenar el modelo

```bash
docker compose run --rm training
```

Esto genera los artefactos en `models/`:

```text
role_model.pkl
imputer.pkl
agent_encoder.pkl
role_encoder.pkl
score_scaler.pkl
feature_columns.pkl
agent_to_role.pkl
metrics.json
dataset_players_processed.csv
```

## 2. Levantar la API de inferencia

```bash
docker compose up --build inference
```

## 3. Probar salud del servicio

```bash
curl http://localhost:3000/health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "service": "VRCE Inference API"
}
```

## 4. Probar predicción

```bash
curl -X POST http://localhost:3000/predict \
-H "Content-Type: application/json" \
-d '{
  "Average Combat Score": 245,
  "Average Damage Per Round": 158.4,
  "Kills Per Round": 0.82,
  "Assists Per Round": 0.31,
  "First Kills Per Round": 0.14,
  "First Deaths Per Round": 0.09,
  "Headshot %": "27.5%",
  "Clutch Success %": "18.2%",
  "Clutches (won/played)": "2/8",
  "KDR": 1.18,
  "Agents": "Jett"
}'
```

Respuesta esperada:

```json
{
  "system": "VRCE",
  "agent": "Jett",
  "role": "Duelist",
  "role_compliance_probability": 0.8732
}
```

El valor exacto puede variar según el entrenamiento.

## Notas técnicas

- El rol se infiere desde el agente cuando no se envía `Role`.
- El endpoint acepta `Kills:Deaths` o `KDR`.
- El endpoint acepta `Clutches (won/played)` y calcula `Clutches_Won` y `Clutch_Success_Ratio`.
- Las columnas porcentuales pueden enviarse como `27.5%`, `27.5` o `0.275`.

## Documentación Swagger

La API de inferencia incluye documentación interactiva con Swagger UI.

Levantar el servicio de inferencia:

```bash
docker compose up --build inference
```

Abrir la documentación en el navegador:

```text
http://localhost:3000/api-docs
```

También se puede consultar la especificación OpenAPI en formato JSON:

```text
http://localhost:3000/swagger.json
```

Endpoints principales:

- `GET /health`: verifica el estado de la API.
- `POST /predict`: recibe las métricas del jugador y devuelve la probabilidad de cumplimiento del rol.

Ejemplo de cuerpo para `POST /predict`:

```json
{
  "Average Combat Score": 245.7,
  "Average Damage Per Round": 158.4,
  "Kills Per Round": 0.82,
  "Assists Per Round": 0.31,
  "First Kills Per Round": 0.14,
  "First Deaths Per Round": 0.09,
  "Headshot %": 27.5,
  "Clutch Success %": 18.2,
  "Clutch_Success_Ratio": 0.25,
  "Clutches_Won": 2,
  "KDR": 1.18,
  "Agents": "Jett",
  "Role": "Duelist"
}
```
