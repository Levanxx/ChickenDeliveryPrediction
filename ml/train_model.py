from pathlib import Path
from typing import Callable, Optional

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor

BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DATA_PATH = BASE_DIR / "data" / "ventas_diarias_2026.csv"

DIAS_MAP = {
    "lunes": 0,
    "martes": 1,
    "miércoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sábado": 5,
    "domingo": 6,
}


def prepare_dataset(live_data_path: Optional[Path] = None):
    frames = [pd.read_csv(BASE_DATA_PATH)]
    if live_data_path and live_data_path.exists():
        frames.append(pd.read_csv(live_data_path))
    data = pd.concat(frames, ignore_index=True)
    data["fecha"] = pd.to_datetime(data["fecha"])
    data = data.sort_values("fecha").drop_duplicates("fecha", keep="last")
    if "dia_semana_num" not in data:
        data["dia_semana_num"] = data["fecha"].dt.weekday
    else:
        data["dia_semana_num"] = data["dia_semana_num"].fillna(data["fecha"].dt.weekday)
    if "dia_semana" in data:
        mapped = data["dia_semana"].map(DIAS_MAP)
        data["dia_semana_num"] = mapped.fillna(data["dia_semana_num"])
    data["mes"] = data["fecha"].dt.month
    data["dia"] = data["fecha"].dt.day
    data["es_feriado"] = data["es_feriado"].fillna(0).astype(int)
    return data


def train_and_save(live_data_path: Optional[Path], model_path: Path, progress_callback: Optional[Callable] = None):
    progress_callback = progress_callback or (lambda **_: None)
    data = prepare_dataset(live_data_path)
    features = data[["dia_semana_num", "mes", "dia", "es_feriado"]]
    target = data[["delivery", "recojo"]]

    progress_callback(progreso=50, etapa="Entrenando Random Forest")
    x_train, x_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    model = MultiOutputRegressor(RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1))
    model.fit(x_train, y_train)

    progress_callback(progreso=80, etapa="Evaluando precisión del modelo")
    predicted = model.predict(x_test)
    metrics = {
        "mae_delivery": round(float(mean_absolute_error(y_test["delivery"], predicted[:, 0])), 2),
        "mae_recojo": round(float(mean_absolute_error(y_test["recojo"], predicted[:, 1])), 2),
        "r2_delivery": round(float(r2_score(y_test["delivery"], predicted[:, 0])), 3),
        "r2_recojo": round(float(r2_score(y_test["recojo"], predicted[:, 1])), 3),
    }

    progress_callback(progreso=95, etapa="Guardando nueva versión del modelo")
    temporary_path = model_path.with_suffix(".tmp")
    joblib.dump(model, temporary_path)
    temporary_path.replace(model_path)
    return {
        "filas_utilizadas": len(data),
        "rango_datos": {"desde": data["fecha"].min().date().isoformat(), "hasta": data["fecha"].max().date().isoformat()},
        "metricas": metrics,
    }


if __name__ == "__main__":
    result = train_and_save(None, BASE_DIR / "ml" / "models" / "modelo_ventas.pkl")
    print(f"Modelo entrenado con {result['filas_utilizadas']} filas")
