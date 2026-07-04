from datetime import date, datetime
from pathlib import Path
from threading import Lock, Thread
from typing import List
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd

from ml.train_model import train_and_save

app = FastAPI(title="ChickenDelivery ML API", version="2.0")

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml" / "models" / "modelo_ventas.pkl"
LIVE_DATA_PATH = BASE_DIR / "data" / "ventas_reales.csv"
STATUS_PATH = BASE_DIR / "ml" / "models" / "training_status.json"

model_lock = Lock()
training_lock = Lock()
modelo = joblib.load(MODEL_PATH)


class PredictionRequest(BaseModel):
    dia_semana_num: int = Field(ge=0, le=7)
    mes: int = Field(ge=1, le=12)
    dia: int = Field(ge=1, le=31)
    es_feriado: int = Field(ge=0, le=1)


class TrainingRecord(BaseModel):
    fecha: date
    delivery: int = Field(ge=0)
    recojo: int = Field(ge=0)
    es_feriado: int = Field(default=0, ge=0, le=1)


class TrainingRequest(BaseModel):
    registros: List[TrainingRecord]
    origen: str = "ChickenDelivery_Backend"


def default_status():
    return {
        "estado": "listo",
        "progreso": 100,
        "etapa": "Modelo disponible",
        "ultimo_entrenamiento": datetime.fromtimestamp(MODEL_PATH.stat().st_mtime).isoformat(),
        "filas_utilizadas": 0,
        "nuevas_filas": 0,
        "rango_datos": None,
        "metricas": {},
        "error": None,
    }


def read_status():
    if not STATUS_PATH.exists():
        return default_status()
    return json.loads(STATUS_PATH.read_text(encoding="utf-8"))


def write_status(**updates):
    status = read_status()
    status.update(updates)
    STATUS_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")


def persist_live_records(records: List[TrainingRecord]):
    incoming = pd.DataFrame([record.model_dump(mode="json") for record in records])
    if LIVE_DATA_PATH.exists():
        existing = pd.read_csv(LIVE_DATA_PATH)
        incoming = pd.concat([existing, incoming], ignore_index=True)
    incoming["fecha"] = pd.to_datetime(incoming["fecha"])
    incoming = incoming.sort_values("fecha").drop_duplicates("fecha", keep="last")
    incoming.to_csv(LIVE_DATA_PATH, index=False, date_format="%Y-%m-%d")
    return incoming


def train_in_background(request: TrainingRequest):
    global modelo
    try:
        write_status(estado="entrenando", progreso=10, etapa="Validando ventas recibidas", error=None)
        live_data = persist_live_records(request.registros)
        write_status(progreso=30, etapa="Consolidando histórico y ventas nuevas", nuevas_filas=len(request.registros))
        result = train_and_save(LIVE_DATA_PATH, MODEL_PATH, progress_callback=write_status)
        with model_lock:
            modelo = joblib.load(MODEL_PATH)
        write_status(
            estado="completado",
            progreso=100,
            etapa="Modelo actualizado y disponible",
            ultimo_entrenamiento=datetime.now().isoformat(),
            filas_utilizadas=result["filas_utilizadas"],
            nuevas_filas=len(request.registros),
            rango_datos=result["rango_datos"],
            metricas=result["metricas"],
            origen=request.origen,
            error=None,
        )
    except Exception as exc:
        write_status(estado="error", progreso=0, etapa="Falló el entrenamiento", error=str(exc))
    finally:
        training_lock.release()


@app.get("/")
def home():
    return {"message": "Chicken Delivery ML API funcionando", "modelo": "disponible"}


@app.post("/predict")
def predict(data: PredictionRequest):
    entrada = pd.DataFrame([{
        "dia_semana_num": 0 if data.dia_semana_num == 7 else data.dia_semana_num,
        "mes": data.mes,
        "dia": data.dia,
        "es_feriado": data.es_feriado,
    }])
    with model_lock:
        prediccion = modelo.predict(entrada)[0]
    delivery = max(0, round(prediccion[0]))
    recojo = max(0, round(prediccion[1]))
    return {"delivery": delivery, "recojo": recojo, "total": delivery + recojo}


@app.get("/training/status")
def training_status():
    return read_status()


@app.post("/training/start", status_code=202)
def start_training(request: TrainingRequest):
    if not request.registros:
        raise HTTPException(status_code=400, detail="No hay ventas nuevas para entrenar")
    if not training_lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="El modelo ya se está entrenando")
    Thread(target=train_in_background, args=(request,), daemon=True).start()
    return {"estado": "entrenando", "registros_recibidos": len(request.registros)}
