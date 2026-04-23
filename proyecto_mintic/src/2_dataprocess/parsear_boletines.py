"""
parsear_boletines.py
Extrae la serie temporal de TD, TO y TGP nacional de los boletines PDF del DANE.
Salida: data/processed/serie_temporal_td.csv  (entrada del modelo Prophet)
"""

import os
import re
import sys
import json
from datetime import datetime
import pandas as pd
import pdfplumber

# Forzar UTF-8 en la salida estándar (necesario en Windows con cp1252)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RUTA_BOLETINES = os.path.join("data", "raw", "dane_boletines")
RUTA_PROCESSED = os.path.join("data", "processed")
RUTA_SALIDA    = os.path.join(RUTA_PROCESSED, "serie_temporal_td.csv")

MESES_MAP = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4,
    "may": 5, "jun": 6, "jul": 7, "ago": 8,
    "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}

PATRON_NOMBRE = re.compile(r"bol-GEIH-([a-z]{3})(\d{4})\.pdf", re.IGNORECASE)

# Patrones extraídos del análisis real de los boletines DANE:
# - TD:  "tasa de desocupación del total nacional fue X,X%"
# - TGP: "participación se ubicó en X,X%" (puede estar al inicio de línea
#         porque "tasa global de" queda al final de la línea anterior)
# - TO:  "tasa de ocupación fue X,X%"  o  "tasa de ocupación en X,X%"
PATRON_TD = re.compile(
    r"(?:desocupaci[oó]n|desempleo)\s+del\s+total\s+nacional\s+fue\s+(\d{1,2}[,\.]\d)",
    re.IGNORECASE,
)
PATRON_TGP = re.compile(
    r"participaci[oó]n\s+se\s+ubic[oó]\s+en\s+(\d{1,2}[,\.]\d)",
    re.IGNORECASE,
)
PATRON_TO = re.compile(
    r"tasa\s+de\s+ocupaci[oó]n\s+(?:fue|en)\s+(\d{1,2}[,\.]\d)",
    re.IGNORECASE,
)

# Rangos razonables para Colombia
RANGO_TD  = (5.0,  25.0)
RANGO_TO  = (45.0, 70.0)
RANGO_TGP = (55.0, 80.0)


# ── Helpers ───────────────────────────────────────────────────────
def extraer_mes_anio(nombre_archivo: str) -> tuple:
    m = PATRON_NOMBRE.match(nombre_archivo)
    if not m:
        return None, None
    return MESES_MAP.get(m.group(1).lower()), int(m.group(2))


def a_float(texto: str) -> float:
    return float(texto.replace(",", "."))


def buscar_patron(patron: re.Pattern, texto: str) -> float | None:
    m = patron.search(texto)
    if m:
        return a_float(m.group(1))
    return None


# ── Extracción principal: texto corrido ───────────────────────────
def extraer_por_texto_corrido(texto: str) -> dict | None:
    """
    Los boletines DANE describen los indicadores nacionales en párrafo de texto:
    '...la tasa de desocupación del total nacional fue 9,7%,
     la tasa global de participación se ubicó en 64,5%
     y la tasa de ocupación en 58,3%...'
    Esta función busca esos patrones específicos.
    """
    td  = buscar_patron(PATRON_TD,  texto)
    tgp = buscar_patron(PATRON_TGP, texto)
    to  = buscar_patron(PATRON_TO,  texto)

    if td is None or tgp is None or to is None:
        return None

    # Validar rangos
    if not RANGO_TD[0]  <= td  <= RANGO_TD[1]:  return None
    if not RANGO_TO[0]  <= to  <= RANGO_TO[1]:  return None
    if not RANGO_TGP[0] <= tgp <= RANGO_TGP[1]: return None

    return {"tasa_desocupacion": td, "tasa_ocupacion": to, "tasa_global_participacion": tgp}


# ── Extracción fallback: tabla con fila "Total nacional" ──────────
def extraer_por_tabla(paginas) -> dict | None:
    """
    Algunos boletines tienen la tabla resumen en las primeras páginas.
    Buscamos la fila que tenga 'Total nacional' y al menos 3 números
    en los rangos esperados.
    """
    pat_num = re.compile(r"(\d{1,2}[,\.]\d)")
    for pagina in paginas:
        for tabla in pagina.extract_tables():
            for fila in tabla:
                fila_texto = " ".join(str(c) for c in fila if c)
                if not re.search(r"total\s*nacional", fila_texto, re.IGNORECASE):
                    continue
                nums = [a_float(m) for m in pat_num.findall(fila_texto)]
                td_cands  = [n for n in nums if RANGO_TD[0]  <= n <= RANGO_TD[1]]
                to_cands  = [n for n in nums if RANGO_TO[0]  <= n <= RANGO_TO[1]]
                tgp_cands = [n for n in nums if RANGO_TGP[0] <= n <= RANGO_TGP[1]]
                if td_cands and to_cands and tgp_cands:
                    return {
                        "tasa_desocupacion":         td_cands[0],
                        "tasa_ocupacion":            to_cands[0],
                        "tasa_global_participacion": tgp_cands[0],
                    }
    return None


# ── Parseo de un PDF ──────────────────────────────────────────────
def parsear_pdf(ruta_pdf: str) -> dict | None:
    nombre    = os.path.basename(ruta_pdf)
    mes, anio = extraer_mes_anio(nombre)
    if mes is None:
        return None

    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            # Concatenar texto de las primeras 5 páginas (el párrafo clave suele estar en p.3)
            texto_total = "\n".join(
                (p.extract_text() or "") for p in pdf.pages[:5]
            )

            indicadores = extraer_por_texto_corrido(texto_total)
            if indicadores is None:
                indicadores = extraer_por_tabla(pdf.pages[:5])

            if indicadores:
                return {
                    "anio":  anio,
                    "mes":   mes,
                    "fecha": f"{anio}-{mes:02d}-01",
                    **indicadores,
                    "fuente_archivo": nombre,
                }
    except Exception as e:
        print(f"    ! Error en {nombre}: {e}")
    return None


# ── Entry point ───────────────────────────────────────────────────
def parsear_boletines():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Parseando boletines PDF DANE...\n")

    if not os.path.exists(RUTA_BOLETINES):
        print(f"  ✗ No existe carpeta: {RUTA_BOLETINES}")
        return

    pdfs = sorted(
        f for f in os.listdir(RUTA_BOLETINES) if f.lower().endswith(".pdf")
    )
    print(f"  PDFs encontrados: {len(pdfs)}\n")

    registros  = []
    sin_datos  = []

    for nombre in pdfs:
        ruta = os.path.join(RUTA_BOLETINES, nombre)
        resultado = parsear_pdf(ruta)
        if resultado:
            registros.append(resultado)
            print(
                f"  ✓ {nombre[:35]:<35} "
                f"TD={resultado['tasa_desocupacion']:5.1f}%  "
                f"TO={resultado['tasa_ocupacion']:5.1f}%  "
                f"TGP={resultado['tasa_global_participacion']:5.1f}%"
            )
        else:
            sin_datos.append(nombre)
            print(f"  ⚠ Sin datos: {nombre}")

    if not registros:
        print("\n  ✗ No se extrajo ningún indicador. Revisar estructura de los PDFs.")
        return

    df = pd.DataFrame(registros).sort_values(["anio", "mes"]).reset_index(drop=True)

    # Calcular variación anual de TD
    df["variacion_anual_td"] = df["tasa_desocupacion"].diff(12).round(2)

    os.makedirs(RUTA_PROCESSED, exist_ok=True)
    df.to_csv(RUTA_SALIDA, index=False, encoding="utf-8-sig")

    # Guardar log de PDFs sin datos
    if sin_datos:
        ruta_log = os.path.join(RUTA_PROCESSED, "boletines_sin_datos.json")
        with open(ruta_log, "w", encoding="utf-8") as f:
            json.dump({"sin_datos": sin_datos, "generado": datetime.now().isoformat()}, f, indent=2)

    print(f"\n{'─'*55}")
    print(f"  ✓ Registros extraídos : {len(df)}")
    print(f"  ⚠ Sin datos           : {len(sin_datos)}")
    print(f"  ✓ Período             : {df['fecha'].min()} → {df['fecha'].max()}")
    print(f"  ✓ Guardado en         : {RUTA_SALIDA}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Parseo completado.")

    return df


if __name__ == "__main__":
    parsear_boletines()
