# ChickenDelivery

Sistema de prediccion de ventas para apoyar la gestion operativa de ChickenDelivery. El modelo estima la cantidad de pedidos del dia siguiente separados por canal:

- `delivery`: pedidos para reparto.
- `recojo`: pedidos para recojo en tienda.
- `total`: suma de ambos canales.

El proyecto nace como apoyo al sistema web de ventas descrito en el informe del curso, cuyo objetivo es reducir el registro manual, centralizar la informacion comercial y dar soporte a decisiones operativas en horarios de alta demanda.

## Estructura del proyecto

```text
ChickenDelivery/
├── data/
│   └── ventas_diarias_2026.csv
├── generator/
│   ├── generator.py
│   └── validator.py
├── ml/
│   ├── api_model.py
│   ├── predict_model.py
│   ├── train_model.py
│   ├── requirements.txt
│   └── models/
│       └── modelo_ventas.pkl
├── docs/
│   └── modelo_prediccion_ventas.md
└── docker-compose.yml
```

## Modelo de prediccion

El modelo se entrena con datos historicos diarios de ventas. Actualmente usa el archivo `data/ventas_diarias_2026.csv`, que contiene ventas por fecha, dia de semana, canal y feriado.

Variables de entrada:

- `dia_semana_num`: dia de la semana en formato numerico, de 0 a 6.
- `mes`: mes de la fecha a predecir.
- `dia`: dia del mes.
- `es_feriado`: indica si la fecha es feriado.

Variables objetivo:

- `delivery`
- `recojo`

Algoritmo utilizado:

- `RandomForestRegressor`
- Envuelto en `MultiOutputRegressor` para predecir los dos canales en una sola ejecucion.

La documentacion completa esta en [docs/modelo_prediccion_ventas.md](docs/modelo_prediccion_ventas.md).

## Flujo de entrenamiento

Durante la etapa actual, el modelo se entrena con la data disponible mientras se construye y valida el sistema.

Cuando el sistema este en funcionamiento, el entrenamiento se ejecutara cada lunes usando la informacion consolidada de toda la semana anterior. Esto permitira que el modelo incorpore cambios recientes en la demanda, como variaciones por promociones, fines de semana, feriados o cambios en el comportamiento de compra.

Entrenar el modelo:

```bash
python ml/train_model.py
```

El entrenamiento genera o actualiza:

```text
ml/models/modelo_ventas.pkl
```

## Prediccion local

Para ejecutar una prediccion simple del dia siguiente:

```bash
python ml/predict_model.py
```

El resultado esperado tiene esta forma:

```json
{
  "delivery": 80,
  "recojo": 55,
  "total": 135
}
```

## API de prediccion

Levantar la API:

```bash
uvicorn ml.api_model:app --reload --port 8000
```

Abrir la documentacion interactiva:

```text
http://localhost:8000/docs
```

Endpoint principal:

```http
POST /predict
```

Ejemplo de entrada:

```json
{
  "dia_semana_num": 1,
  "mes": 5,
  "dia": 19,
  "es_feriado": 0
}
```

### Reentrenamiento incremental

La API mantiene el modelo base intacto y guarda la versión entrenada en
`ml/models/runtime/`. Las ventas reales recibidas se consolidan por fecha en
`data/ventas_reales.csv`; ambos artefactos son locales y están ignorados por Git.

Endpoints disponibles:

```http
GET  /training/status
POST /training/start
```

`POST /training/start` recibe ventas diarias agregadas:

```json
{
  "origen": "Entrenamiento automático semanal",
  "registros": [
    {"fecha": "2026-07-04", "delivery": 3, "recojo": 3, "es_feriado": 0}
  ]
}
```

El entrenamiento se ejecuta en segundo plano. `GET /training/status` informa
la etapa, progreso, filas utilizadas, rango de fechas, métricas y errores. El
backend de ChickenDelivery programa el envío cada lunes a las 00:05 usando las
ventas consolidadas de la semana anterior.

Ejemplo de salida:

```json
{
  "delivery": 76,
  "recojo": 48,
  "total": 124
}
```

## Instalacion

Crear y activar un entorno virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

En Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Contexto del proyecto

El informe del proyecto identifica que Ikigai Deli Express EIRL gestiona pedidos principalmente por WhatsApp y luego registra la informacion manualmente. Ese flujo genera cuellos de botella, retrasos y riesgo de errores cuando la demanda aumenta.

El modelo de prediccion complementa el sistema web porque permite anticipar la demanda del dia siguiente. Con esa informacion, el negocio puede preparar mejor la atencion, estimar carga operativa y organizar recursos antes de los horarios de mayor venta.
