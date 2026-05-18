# Documentacion del modelo de prediccion de ventas

## 1. Proposito

El modelo de prediccion de ventas de ChickenDelivery tiene como objetivo estimar la demanda del dia siguiente. La prediccion se separa por canal de atencion:

- `delivery`: cantidad esperada de pedidos para reparto.
- `recojo`: cantidad esperada de pedidos para recojo en tienda.
- `total`: suma de `delivery` y `recojo`.

Esta prediccion busca apoyar la toma de decisiones operativas del negocio, especialmente en la planificacion de atencion, preparacion de productos y organizacion del personal antes de los horarios de mayor demanda.

## 2. Contexto del negocio

El informe del proyecto describe la necesidad de optimizar el proceso de ventas de Ikigai Deli Express EIRL. Actualmente, el negocio depende de canales manuales como WhatsApp para recibir pedidos y luego registrar la informacion en una intranet. Este proceso puede generar:

- Congestion en horas punta.
- Demoras en la atencion.
- Errores al registrar precios, productos o pedidos.
- Perdida o duplicidad de informacion.
- Falta de datos estructurados para tomar decisiones.

El modelo se incorpora como una capacidad analitica del sistema web. Al convertir las ventas diarias en datos estructurados, el sistema puede anticipar la demanda y reducir la improvisacion operativa.

## 3. Alcance del modelo

El modelo predice ventas agregadas por dia. No predice todavia:

- Ventas por producto especifico.
- Inventario detallado por insumo o receta.
- Rutas de reparto.
- Comportamiento individual de clientes.
- Cancelaciones o tiempos de entrega.

Su alcance actual es estimar la demanda general del dia siguiente por canal de venta.

## 4. Datos utilizados

El dataset actual se encuentra en:

```text
data/ventas_diarias_2026.csv
```

Columnas principales:

| Columna | Descripcion |
| --- | --- |
| `fecha` | Fecha de la venta diaria. |
| `dia_semana` | Nombre del dia de la semana. |
| `delivery` | Cantidad de pedidos por delivery. |
| `recojo` | Cantidad de pedidos por recojo. |
| `total` | Total diario de pedidos. |
| `es_feriado` | Indicador de feriado: `1` si es feriado, `0` si no lo es. |

Durante la etapa actual, el modelo se entrena con los datos disponibles del proyecto. Cuando el sistema este en produccion, la fuente ideal sera la data real generada por el sistema web de ventas.

## 5. Preparacion de datos

El archivo `ml/train_model.py` realiza los siguientes pasos:

1. Carga el dataset `data/ventas_diarias_2026.csv`.
2. Convierte la columna `fecha` a formato de fecha.
3. Convierte el nombre del dia de semana a un numero:

| Dia | Valor |
| --- | --- |
| lunes | 0 |
| martes | 1 |
| miércoles | 2 |
| jueves | 3 |
| viernes | 4 |
| sábado | 5 |
| domingo | 6 |

4. Extrae el mes desde `fecha`.
5. Extrae el dia del mes desde `fecha`.
6. Define variables de entrada y variables objetivo.

Variables de entrada:

```text
dia_semana_num, mes, dia, es_feriado
```

Variables objetivo:

```text
delivery, recojo
```

## 6. Algoritmo

El modelo utiliza:

```text
MultiOutputRegressor(RandomForestRegressor)
```

La eleccion permite predecir dos valores relacionados en una misma ejecucion:

- pedidos por delivery
- pedidos por recojo

`RandomForestRegressor` es adecuado para esta etapa porque funciona bien con datasets tabulares, captura relaciones no lineales y no requiere una normalizacion compleja de las variables de entrada.

Configuracion actual:

```python
RandomForestRegressor(n_estimators=150, random_state=42)
```

## 7. Entrenamiento

Script principal:

```text
ml/train_model.py
```

Comando:

```bash
python ml/train_model.py
```

Salida del entrenamiento:

```text
ml/models/modelo_ventas.pkl
```

Este archivo contiene el modelo entrenado y es utilizado tanto por el script de prediccion local como por la API.

## 8. Reentrenamiento semanal

Durante la construccion del proyecto, el modelo se entrena con la data disponible.

Cuando el sistema este en funcionamiento, el reentrenamiento se realizara cada lunes usando la data de toda la semana anterior. El flujo esperado es:

1. El sistema registra ventas reales de lunes a domingo.
2. El lunes se consolida la data de la semana anterior.
3. Se actualiza el dataset historico.
4. Se ejecuta `ml/train_model.py`.
5. Se reemplaza `ml/models/modelo_ventas.pkl` por la nueva version entrenada.
6. La API usa el modelo actualizado para predecir las ventas del dia siguiente.

Este ciclo permite que el modelo aprenda de patrones recientes y se ajuste gradualmente a cambios en la demanda.

## 9. Prediccion local

Script:

```text
ml/predict_model.py
```

Comando:

```bash
python ml/predict_model.py
```

El script calcula automaticamente la fecha de mañana y arma la entrada del modelo con:

- dia de semana de mañana
- mes de mañana
- dia del mes de mañana
- feriado configurado manualmente como `0`

Salida esperada:

```json
{
  "delivery": 80,
  "recojo": 55,
  "total": 135
}
```

## 10. API

La API esta implementada en:

```text
ml/api_model.py
```

Levantar servidor:

```bash
uvicorn ml.api_model:app --reload --port 8000
```

Documentacion interactiva:

```text
http://localhost:8000/docs
```

Endpoint:

```http
POST /predict
```

Entrada:

```json
{
  "dia_semana_num": 1,
  "mes": 5,
  "dia": 19,
  "es_feriado": 0
}
```

Salida:

```json
{
  "delivery": 76,
  "recojo": 48,
  "total": 124
}
```

## 11. Uso operativo esperado

El modelo puede usarse de esta manera dentro del sistema:

1. Al cierre del dia, el sistema guarda las ventas reales.
2. Antes de iniciar la operacion del siguiente dia, se consulta la prediccion.
3. El administrador visualiza la demanda esperada.
4. El negocio prepara recursos segun el volumen estimado:
   - personal de atencion
   - productos listos para venta
   - capacidad de reparto
   - horarios de mayor control

## 12. Limitaciones actuales

El modelo actual depende de pocas variables de entrada. Por eso, sus predicciones pueden mejorar cuando se incorporen mas datos reales del negocio.

Limitaciones identificadas:

- El indicador de feriados aun se ingresa manualmente en la prediccion local.
- No se consideran promociones, clima, campañas o eventos especiales.
- No se predice por producto, solo por canal.
- La precision dependera de la calidad y cantidad de datos historicos.
- El dataset actual debe reemplazarse o enriquecerse progresivamente con ventas reales del sistema.

## 13. Mejoras recomendadas

Para siguientes iteraciones se recomienda:

- Automatizar el calendario de feriados de Peru.
- Registrar promociones y dias de campaña como variables de entrada.
- Agregar ventas por producto para predecir demanda por plato o combo.
- Guardar metricas de evaluacion del modelo, como MAE o RMSE.
- Versionar modelos entrenados por fecha.
- Crear un proceso automatico de reentrenamiento cada lunes.
- Conectar la API con el dashboard administrativo del sistema web.

## 14. Relacion con los objetivos del proyecto

El modelo contribuye al objetivo general del sistema web porque convierte la informacion de ventas en una herramienta de decision. Ademas, apoya los objetivos especificos relacionados con:

- Centralizar informacion de ventas.
- Reducir desorganizacion en horas de alta demanda.
- Visualizar informacion comercial mediante reportes.
- Mejorar la atencion y la preparacion operativa del negocio.
