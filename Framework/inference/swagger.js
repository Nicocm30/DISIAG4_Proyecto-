const swaggerJSDoc = require("swagger-jsdoc");

const swaggerDefinition = {
  openapi: "3.0.0",
  info: {
    title: "VRCE Inference API",
    version: "1.0.0",
    description:
      "API de inferencia para estimar la probabilidad de cumplimiento del rol de un jugador en Valorant mediante el sistema VRCE."
  },
  servers: [
    {
      url: "http://localhost:3000",
      description: "Servidor local"
    }
  ],
  tags: [
    {
      name: "Health",
      description: "Verificación del estado del servicio"
    },
    {
      name: "Prediction",
      description: "Predicción de cumplimiento del rol"
    }
  ],
  components: {
    schemas: {
      HealthResponse: {
        type: "object",
        properties: {
          status: {
            type: "string",
            example: "ok"
          },
          service: {
            type: "string",
            example: "VRCE Inference API"
          }
        }
      },
      PredictionRequest: {
        type: "object",
        required: [
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
          "Agents"
        ],
        properties: {
          "Average Combat Score": {
            type: "number",
            example: 245.7,
            description: "Puntaje promedio de combate del jugador."
          },
          "Average Damage Per Round": {
            type: "number",
            example: 158.4,
            description: "Daño promedio causado por ronda."
          },
          "Kills Per Round": {
            type: "number",
            example: 0.82,
            description: "Eliminaciones promedio por ronda."
          },
          "Assists Per Round": {
            type: "number",
            example: 0.31,
            description: "Asistencias promedio por ronda."
          },
          "First Kills Per Round": {
            type: "number",
            example: 0.14,
            description: "Primeras eliminaciones promedio por ronda."
          },
          "First Deaths Per Round": {
            type: "number",
            example: 0.09,
            description: "Primeras muertes promedio por ronda."
          },
          "Headshot %": {
            type: "number",
            example: 27.5,
            description: "Porcentaje de disparos a la cabeza."
          },
          "Clutch Success %": {
            type: "number",
            example: 18.2,
            description: "Porcentaje de éxito en situaciones de clutch."
          },
          "Clutch_Success_Ratio": {
            type: "number",
            example: 0.25,
            description: "Ratio de clutches ganados respecto a clutches jugados."
          },
          "Clutches_Won": {
            type: "number",
            example: 2,
            description: "Número de clutches ganados."
          },
          "KDR": {
            type: "number",
            example: 1.18,
            description: "Relación entre eliminaciones y muertes."
          },
          "Agents": {
            type: "string",
            example: "Jett",
            description: "Agente utilizado por el jugador. El rol se puede inferir desde este campo."
          },
          "Role": {
            type: "string",
            example: "Duelist",
            description: "Rol del jugador. Es opcional si el sistema puede inferirlo desde el agente."
          }
        }
      },
      PredictionResponse: {
        type: "object",
        properties: {
          system: {
            type: "string",
            example: "VRCE"
          },
          agent: {
            type: "string",
            example: "Jett"
          },
          role: {
            type: "string",
            example: "Duelist"
          },
          role_compliance_probability: {
            type: "number",
            example: 0.8732,
            description: "Probabilidad normalizada de cumplimiento del rol en el rango [0,1]."
          }
        }
      },
      ErrorResponse: {
        type: "object",
        properties: {
          error: {
            type: "string",
            example: "Prediction failed"
          },
          details: {
            type: "string",
            example: "Agente no visto durante entrenamiento: UnknownAgent"
          }
        }
      }
    }
  },
  paths: {
    "/health": {
      get: {
        tags: ["Health"],
        summary: "Verifica el estado de la API",
        description: "Devuelve el estado básico del servicio de inferencia.",
        responses: {
          200: {
            description: "Servicio disponible",
            content: {
              "application/json": {
                schema: {
                  $ref: "#/components/schemas/HealthResponse"
                }
              }
            }
          }
        }
      }
    },
    "/predict": {
      post: {
        tags: ["Prediction"],
        summary: "Predice la probabilidad de cumplimiento del rol",
        description:
          "Recibe métricas del jugador y devuelve la probabilidad de cumplimiento del rol estimada por el modelo entrenado.",
        requestBody: {
          required: true,
          content: {
            "application/json": {
              schema: {
                $ref: "#/components/schemas/PredictionRequest"
              }
            }
          }
        },
        responses: {
          200: {
            description: "Predicción generada correctamente",
            content: {
              "application/json": {
                schema: {
                  $ref: "#/components/schemas/PredictionResponse"
                }
              }
            }
          },
          500: {
            description: "Error durante la predicción",
            content: {
              "application/json": {
                schema: {
                  $ref: "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    }
  }
};

const options = {
  swaggerDefinition,
  apis: []
};

module.exports = swaggerJSDoc(options);
