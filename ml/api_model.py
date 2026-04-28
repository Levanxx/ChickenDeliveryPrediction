from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
import joblib

app = FastAPI(title="ChickenDelivery ML API")

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml" / "models" / "modelo_ventas.pkl"

modelo = joblib.load(MODEL_PATH)


class PredictionRequest(BaseModel):
    dia_semana_num: int
    mes: int
    dia: int
    es_feriado: int


@app.get("/")
def home():
    return {
        "message": "Chicken Delivery ML API funcionando"
    }


@app.post("/predict")
def predict(data: PredictionRequest):
    entrada = pd.DataFrame([{
        "dia_semana_num": data.dia_semana_num,
        "mes": data.mes,
        "dia": data.dia,
        "es_feriado": data.es_feriado
    }])

    prediccion = modelo.predict(entrada)[0]

    delivery = max(0, round(prediccion[0]))
    recojo = max(0, round(prediccion[1]))

    return {
        "delivery": delivery,
        "recojo": recojo,
        "total": delivery + recojo
    }