import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor

# Cargar dataset
df = pd.read_csv("data/ventas_diarias_2026.csv")

# Convertir fecha
df["fecha"] = pd.to_datetime(df["fecha"])

# Mapear días a número
dias_map = {
    "lunes": 0,
    "martes": 1,
    "miércoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sábado": 5,
    "domingo": 6
}

df["dia_semana_num"] = df["dia_semana"].map(dias_map)

# Features nuevas
df["mes"] = df["fecha"].dt.month
df["dia"] = df["fecha"].dt.day

# Variables de entrada
X = df[["dia_semana_num", "mes", "dia", "es_feriado"]]

# Variables objetivo
y = df[["delivery", "recojo"]]

# Modelo
modelo = MultiOutputRegressor(
    RandomForestRegressor(n_estimators=150, random_state=42)
)

# Entrenamiento
modelo.fit(X, y)

# Guardar modelo
joblib.dump(modelo, "ml/models/modelo_ventas.pkl")

print("Modelo entrenado y guardado")