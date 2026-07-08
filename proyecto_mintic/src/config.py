"""Parámetros globales y rutas del proyecto."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Rutas base
ROOT_DIR = Path(__file__).parent.parent
DATA_RAW = ROOT_DIR / "data" / "01_raw"
DATA_INTERMEDIATE = ROOT_DIR / "data" / "02_intermediate"
DATA_PRIMARY = ROOT_DIR / "data" / "03_primary"
DATA_OUTPUT = ROOT_DIR / "data" / "04_model_output"
MODELS_DIR = ROOT_DIR / "models"
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Crear directorios si no existen
for d in [DATA_INTERMEDIATE, DATA_PRIMARY, DATA_OUTPUT, MODELS_DIR, FIGURES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Base de datos
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "database": os.getenv("POSTGRES_DB", "mintic_db"),
    "user": os.getenv("POSTGRES_USER", "mintic_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "mintic2026"),
}

# URLs de datos abiertos
SENA_API_URL = os.getenv("SENA_API_URL", "https://www.datos.gov.co/resource/8pqf-rmzr.json")
SENA_API_LIMIT = 10_000

# Parámetros del modelo
MODEL_CONFIG = {
    "seasonal_periods": 12,
    "trend": "add",
    "seasonal": "add",
    "train_ratio": 0.80,
    "forecast_horizon": 6,
    "confidence_level": 0.90,
    "mae_threshold": 1.0,
    "rmse_threshold": 1.5,
}

# Rangos de validación de indicadores DANE
VALIDATION_RANGES = {
    "tasa_desocupacion": (5.0, 25.0),
    "tasa_ocupacion": (45.0, 70.0),
    "tasa_global_participacion": (55.0, 80.0),
}
