import pandas as pd
import joblib
from datetime import datetime, timedelta

modelo = joblib.load("ml/models/modelo_ventas.pkl")

mañana = datetime.now() + timedelta(days=1)

datos = pd.DataFrame([{
    "dia_semana_num": mañana.weekday(),
    "mes": mañana.month,
    "dia": mañana.day,
    "es_feriado": 0  # se puede automatizar
}])

pred = modelo.predict(datos)[0]

delivery = int(pred[0])
recojo = int(pred[1])

print({
    "delivery": delivery,
    "recojo": recojo,
    "total": delivery + recojo
})