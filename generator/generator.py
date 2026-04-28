import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Config
fecha_inicio = datetime(2026, 1, 1)
fecha_fin = datetime(2026, 4, 28)

# Feriados en Perú 
feriados = [
    "2026-01-01",  # Año Nuevo
    "2026-12-25",  # Navidad

]

feriados = [pd.to_datetime(f) for f in feriados]

data = []

fecha = fecha_inicio
total_acumulado = 0
META_TOTAL = 10000

while fecha <= fecha_fin:
    dia_semana_num = fecha.weekday()
    dia_semana_nombre = fecha.strftime("%A")

    # Convertir a español
    dias_es = {
        "Monday": "lunes",
        "Tuesday": "martes",
        "Wednesday": "miércoles",
        "Thursday": "jueves",
        "Friday": "viernes",
        "Saturday": "sábado",
        "Sunday": "domingo"
    }
    dia_semana = dias_es[dia_semana_nombre]

    es_feriado = 1 if fecha in feriados else 0

    # 🔥 lógica de negocio realista
    if dia_semana_num >= 4:  # viernes, sábado, domingo
        delivery = np.random.randint(60, 120)
        recojo = np.random.randint(40, 90)
    else:
        delivery = np.random.randint(30, 70)
        recojo = np.random.randint(20, 50)

    # boost por feriado
    if es_feriado:
        delivery *= 1.3
        recojo *= 1.2

    delivery = int(delivery)
    recojo = int(recojo)

    total = delivery + recojo
    total_acumulado += total

    data.append({
        "fecha": fecha.strftime("%Y-%m-%d"),
        "dia_semana": dia_semana,
        "delivery": delivery,
        "recojo": recojo,
        "total": total,
        "es_feriado": es_feriado
    })

    fecha += timedelta(days=1)

# Ajuste para que el total sea cercano a 10,000
df = pd.DataFrame(data)

factor = META_TOTAL / df["total"].sum()
df["delivery"] = (df["delivery"] * factor).astype(int)
df["recojo"] = (df["recojo"] * factor).astype(int)
df["total"] = df["delivery"] + df["recojo"]

# Guardar
df.to_csv("ventas_diarias_2026.csv", index=False)

print("Dataset generado 🔥")
print("Total ventas:", df["total"].sum())