# Arquitectura del Sistema

## Diagrama general

```
┌─────────────────────────────────────────────────────────────────┐
│                        FUENTES DE DATOS                         │
│  datos.gov.co (SENA)  │  dane.gov.co (PDF)  │  filco.mintrabajo │
└──────────┬────────────┴────────┬────────────┴────────┬──────────┘
           │                    │                      │
           ▼                    ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    F1 · DATASOURCE (Python)                     │
│  extraccion_sena.py  │  extraccion_dane_boletines.py  │         │
│  extraccion_geih.py  │  extraccion_filco.py           │         │
└──────────────────────────────┬──────────────────────────────────┘
                               │  data/raw/
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    F2 · DATAPROCESS (Python)                    │
│         validar_datos.py  →  parsear_boletines.py               │
│         metadata.json        serie_temporal_td.csv              │
└──────────────────────────────┬──────────────────────────────────┘
                               │  data/processed/
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│               F3 · DATATRANSFORM (PySpark + Docker)             │
│    transformar.py (PySpark + JDBC)                              │
│    transformar_informalidad.py (psycopg2)                       │
│    DDL: crear_tablas.sql → agregar_coordenadas.sql              │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              PostgreSQL 15 — mintic_db (Docker)                 │
│  dim_periodo  │  dim_departamento  │  dim_ciudad                │
│  fact_mercado_laboral  │  fact_informalidad  │  fact_demanda_sena│
│  prediccion_td                                                   │
└──────────────────┬────────────────────────┬─────────────────────┘
                   │                        │
                   ▼                        ▼
┌──────────────────────────┐  ┌────────────────────────────────────┐
│  F4 · DATAPRODUCT (IA)   │  │      VISUALIZACIÓN                 │
│  modelo_prophet.py       │  │  Web App: economia-empleo.vercel.app│
│  Holt-Winters / Prophet  │  │  Power BI: dashboard_mintic.pbix   │
│  MAE=0,43pp RMSE=0,54pp  │  │  5 secciones interactivas          │
└──────────────────────────┘  └────────────────────────────────────┘
```

---

## Componentes de infraestructura

### Contenedores Docker

```yaml
# docker-compose.yml
services:
  postgres:      # PostgreSQL 15 — puerto 5432
  jupyter:       # PySpark Notebook — puerto 8888
  adminer:       # Interfaz web BD — puerto 8081
```

Todos los contenedores comparten la red `mintic_net`. Las tablas DDL se ejecutan automáticamente al iniciar el contenedor de postgres mediante el volumen `/docker-entrypoint-initdb.d`.

### Web App (Next.js + Vercel)

- **Repositorio:** `pagina_web/` en la raíz del repo
- **Deploy:** automático en Vercel al hacer push a `main`
- **URL producción:** https://economia-empleo.vercel.app
- **Secciones:** Panorama Nacional / Tendencia e Informalidad / Demanda SENA / Predicción IA / ANOVA Estadístico

### Pipeline de datos

| Script | Tecnología | Input | Output |
|---|---|---|---|
| `extraccion_sena.py` | requests / Socrata API | datos.gov.co | `sena_inscritos.csv` |
| `extraccion_dane_boletines.py` | requests | dane.gov.co | 34 PDFs |
| `extraccion_filco.py` | Selenium | filco.mintrabajo.gov.co | Excel EISS |
| `validar_datos.py` | pandas | `data/raw/` | `metadata.json` |
| `parsear_boletines.py` | pdfplumber + regex | 34 PDFs | `serie_temporal_td.csv` |
| `transformar.py` | PySpark + JDBC | `data/raw/` + `data/processed/` | PostgreSQL |
| `transformar_informalidad.py` | psycopg2 | Excel EISS | PostgreSQL |
| `modelo_prophet.py` | statsmodels / Prophet | `serie_temporal_td.csv` | `prediccion_td` (tabla + CSV + PNG) |

---

## Modelo de datos — Esquema estrella

```
         dim_periodo ◄──────────────────────────────────┐
              │                                          │
              ▼                                          │
dim_departamento ──► fact_mercado_laboral                │
                     fact_demanda_sena                   │
                                                         │
dim_ciudad ──────► fact_informalidad ───────────────────►┘
                   prediccion_td (sin FK de dimensión, autónoma)
```

El esquema estrella permite que Power BI y la web app hagan consultas eficientes sin joins costosos en la capa de visualización.

---

## Flujo de actualización mensual

```
1. DANE publica nuevo boletín PDF (~día 30 del mes siguiente)
2. Descargar PDF → data/raw/dane_boletines/
3. python src/2_dataprocess/parsear_boletines.py
4. python src/3_datatransform/transformar.py  (dentro del Jupyter container)
5. python src/4_dataproduct/modelo_prophet.py
6. Web app en Vercel se actualiza automáticamente
```

Tiempo estimado de actualización: ~15 minutos.
