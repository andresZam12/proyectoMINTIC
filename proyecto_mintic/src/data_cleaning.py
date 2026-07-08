"""Limpieza y tratamiento de datos crudos."""
import pandas as pd
import numpy as np
from src.config import VALIDATION_RANGES

SENA_COL_MAP = {
    "nombre_de_la_ocupaci_n": "ocupacion",
    "n_mero_de_inscritos_2019": "inscritos_2019",
    "n_mero_de_inscritos_2020": "inscritos_2020",
}


def clean_sena(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el dataset SENA: renombra columnas con encoding especial, convierte tipos."""
    rename = {k: v for k, v in SENA_COL_MAP.items() if k in df.columns}
    df = df.rename(columns=rename).copy()

    for col in ["inscritos_2019", "inscritos_2020"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    if "ocupacion" in df.columns:
        df["ocupacion"] = df["ocupacion"].str.strip().str.title()

    df = df.dropna(subset=["ocupacion"])
    return df


def clean_serie_temporal(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia la serie temporal: tipos, rangos y columnas derivadas."""
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.sort_values("fecha").reset_index(drop=True)

    for col, (vmin, vmax) in VALIDATION_RANGES.items():
        if col in df.columns:
            mask = (df[col] < vmin) | (df[col] > vmax)
            if mask.any():
                df.loc[mask, col] = np.nan
                df[col] = df[col].interpolate(method="linear")

    if "variacion_anual_td" not in df.columns:
        df["variacion_anual_td"] = df["tasa_desocupacion"].diff(12).round(2)

    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    df["trimestre"] = df["fecha"].dt.quarter

    return df


def remove_duplicates(df: pd.DataFrame, subset: list) -> pd.DataFrame:
    """Elimina filas duplicadas basado en columnas clave."""
    before = len(df)
    df = df.drop_duplicates(subset=subset).reset_index(drop=True)
    removed = before - len(df)
    if removed:
        print(f"  Duplicados eliminados: {removed}")
    return df
