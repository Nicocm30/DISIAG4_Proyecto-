# Documentación del proyecto dividida por hitos

## Hito 1: Definición del problema y alcance

En este primer hito se establece una comprensión clara del problema que se desea resolver mediante técnicas de Machine Learning. Esto implica identificar la necesidad o situación específica, definir los objetivos del proyecto y determinar qué tipo de solución se espera obtener.

Además, se delimita el alcance del proyecto, especificando qué aspectos serán abordados y cuáles quedan fuera. Se deben identificar las variables relevantes, los posibles usuarios o stakeholders, y el impacto esperado de la solución. También es importante definir criterios de éxito y métricas iniciales que permitirán evaluar si el problema está siendo resuelto adecuadamente.

En esta etapa se busca responder preguntas clave como:
- ¿Cuál es el problema concreto?
- ¿Por qué es importante resolverlo?
- ¿Qué tipo de modelo o enfoque podría ser adecuado?
- ¿Qué limitaciones existen (tiempo, recursos, datos)?

---

## Hito 2: Los datos (origen, descripción y análisis)

Este hito se enfoca en la obtención y comprensión de los datos que serán utilizados para entrenar el modelo. Se describe el origen de los datos (bases de datos, APIs, archivos, sensores, etc.) y se documenta su estructura, formato y características principales.

Se realiza un análisis exploratorio de datos (EDA) para entender patrones, distribuciones, relaciones entre variables y posibles problemas como valores faltantes, datos atípicos o inconsistencias. Esta fase es clave para evaluar la calidad de los datos y determinar si son adecuados para el problema planteado.

También se pueden aplicar procesos de limpieza y transformación, como:
- Eliminación o imputación de valores nulos
- Normalización o estandarización
- Codificación de variables categóricas
- Generación de nuevas variables (feature engineering)

El objetivo principal es preparar un conjunto de datos limpio, consistente y representativo que permita entrenar modelos de manera efectiva.

---

## Hito 3: Experimentación y validación del modelo ML

En este hito se desarrollan, entrenan y evalúan distintos modelos de Machine Learning para resolver el problema definido. Se seleccionan algoritmos adecuados según la naturaleza del problema (clasificación, regresión, clustering, etc.) y se realizan múltiples experimentos para comparar su desempeño.

Se divide el conjunto de datos en subconjuntos (entrenamiento, validación y prueba) para evitar el sobreajuste y asegurar una evaluación objetiva. Se utilizan métricas específicas (accuracy, precision, recall, F1-score, RMSE, entre otras) para medir el rendimiento del modelo.

También se pueden aplicar técnicas como:
- Ajuste de hiperparámetros
- Validación cruzada
- Selección de características
- Ensambles de modelos

Se selecciona el modelo que mejor balancea desempeño y generalización, y se documentan los resultados, conclusiones y posibles mejoras futuras.

---
# Notebook

Contenido de ejecución en lenguaje Python, contiene data lake (datos sin procesar, archivos csv) para realizar el análisis y entrenamiento del modelo ML del proyecto VPER.
