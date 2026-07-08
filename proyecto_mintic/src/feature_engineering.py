"""Creación de variables derivadas y features para el modelo."""
import pandas as pd
import numpy as np


def add_lag_features(df: pd.DataFrame, col: str, lags: list[int]) -> pd.DataFrame:
    """Agrega variables rezagadas (lags) de una columna."""
    df = df.copy()
    for lag in lags:
        df[f"{col}_lag{lag}"] = df[col].shift(lag)
    return df


def add_rolling_features(df: pd.DataFrame, col: str, windows: list[int]) -> pd.DataFrame:
    """Agrega medias móviles de una columna."""
    df = df.copy()
    for w in windows:
        df[f"{col}_ma{w}"] = df[col].rolling(window=w, min_periods=1).mean().round(3)
    return df


def add_seasonal_dummies(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega variables dummy para mes (estacionalidad)."""
    df = df.copy()
    if "mes" not in df.columns:
        df["mes"] = pd.to_datetime(df["fecha"]).dt.month
    mes_dummies = pd.get_dummies(df["mes"], prefix="mes", drop_first=True)
    return pd.concat([df, mes_dummies], axis=1)


def add_annual_variation(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Calcula variación interanual en puntos porcentuales."""
    df = df.copy()
    df[f"{col}_var_anual"] = df[col].diff(12).round(2)
    return df


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Construye la matriz de features completa para el modelo."""
    df = add_lag_features(df, "tasa_desocupacion", lags=[1, 2, 3, 12])
    df = add_rolling_features(df, "tasa_desocupacion", windows=[3, 6])
    df = add_annual_variation(df, "tasa_desocupacion")
    df = add_seasonal_dummies(df)
    return df.dropna().reset_index(drop=True)
