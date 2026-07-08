# Guía de Validación y Reproducción

Esta guía permite a cualquier evaluador reproducir el proyecto desde cero y verificar los resultados.

## Requisitos previos

| Herramienta | Versión mínima | Para qué |
|---|---|---|
| Python | 3.11+ | Scripts de extracción, procesamiento y modelo |
| Docker Desktop | Cualquier versión reciente | PostgreSQL + Jupyter + Adminer |
| Google Chrome + ChromeDriver | Versión compatible | Scripts con Selenium (FILCO, GEIH) |
| Git | Cualquier | Clonar el repositorio |

## Paso 1 — Clonar y configurar

```bash
git clone https://github.com/andresZam12/proyectoMINTIC.git
cd proyectoMINTIC/proyecto_mintic

# Instalar dependencias Python
pip install -r requirements.txt
```

El archivo `.env` con credenciales ya está incluido en la raíz del proyecto. Si no existe, crearlo con:
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mintic_db
POSTGRES_USER=mintic_user
POSTGRES_PASSWORD=mintic2026
```

## Paso 2 — Levantar la infraestructura

```bash
docker-compose up -d
```

Verificar que los tres contenedores están corriendo:
```bash
docker ps
# Debe mostrar: mintic_postgres, mintic_jupyter, mintic_adminer
```

Las tablas DDL se crean automáticamente al iniciar el contenedor de PostgreSQL.

**Accesos:**
- Adminer (interfaz web BD): http://localhost:8081 → servidor: `postgres`, usuario: `mintic_user`, contraseña: `mintic2026`, BD: `mintic_db`
- Jupyter Lab: http://localhost:8888 (token: `mintic2026`)

## Paso 3 — Extracción de datos

```bash
# Dataset SENA desde datos.gov.co (obligatorio, ~30 segundos)
python src/1_datasource/extraccion_sena.py

# Boletines PDF del DANE (~5 minutos, descarga 34 archivos)
python src/1_datasource/extraccion_dane_boletines.py

# Informalidad FILCO — requiere Chrome (opcional, se puede descargar manualmente)
python src/1_datasource/extraccion_filco.py
```

> **Nota:** Si el script de FILCO es bloqueado por el portal, los archivos Excel pueden descargarse manualmente desde https://filco.mintrabajo.gov.co y depositarse en `data/raw/filco/`.

## Paso 4 — Validación y procesamiento

```bash
# Validar integridad del data lake (genera metadata.json)
python src/2_dataprocess/validar_datos.py

# Extraer tasas de los PDFs → serie_temporal_td.csv
python src/2_dataprocess/parsear_boletines.py
```

Verificar que `data/processed/serie_temporal_td.csv` tiene al menos 30 filas con columnas `fecha`, `tasa_desocupacion`, `tasa_ocupacion`, `tasa_global_participacion`.

## Paso 5 — Transformación y carga a PostgreSQL

```bash
# Cargar datos de informalidad (se ejecuta localmente)
python src/3_datatransform/transformar_informalidad.py

# Cargar resto de datos con PySpark (ejecutar dentro del contenedor Jupyter)
# Opción A: desde línea de comandos
docker exec -it mintic_jupyter spark-submit /home/jovyan/src/3_datatransform/transformar.py

# Opción B: abrir Jupyter en http://localhost:8888 y ejecutar el script desde un notebook
```

## Paso 6 — Modelo de predicción

```bash
python src/4_dataproduct/modelo_prophet.py
```

**Resultados esperados:**
- `data/processed/prediccion_td.csv` — predicciones a 6 meses
- `data/processed/forecast_prophet.png` — gráfica de la serie + forecast
- Tabla `prediccion_td` en PostgreSQL con MAE ≈ 0,43 pp y RMSE ≈ 0,54 pp

## Verificación de resultados

### Consultas SQL de validación

```sql
-- Verificar carga de datos históricos
SELECT COUNT(*) FROM fact_mercado_laboral;

-- Ver predicciones del modelo
SELECT fecha, td_predicha, td_lower, td_upper, mae, rmse
FROM prediccion_td
ORDER BY fecha;

-- Top 10 ocupaciones SENA
SELECT ocupacion, SUM(inscritos) as total
FROM fact_demanda_sena
GROUP BY ocupacion
ORDER BY total DESC
LIMIT 10;

-- Informalidad por ciudad (últimos datos disponibles)
SELECT c.ciudad, f.tasa_informalidad, f.sexo
FROM fact_informalidad f
JOIN dim_ciudad c ON f.id_ciudad = c.id_ciudad
JOIN dim_periodo p ON f.id_periodo = p.id_periodo
WHERE p.anio = (SELECT MAX(anio) FROM dim_periodo WHERE id_periodo IN (SELECT id_periodo FROM fact_informalidad))
ORDER BY f.tasa_informalidad DESC;
```

### Valores esperados

| Verificación | Valor esperado |
|---|---|
| Filas en `serie_temporal_td.csv` | ~34 filas (may 2023 – feb 2026) |
| MAE en tabla `prediccion_td` | ~0,43 pp |
| RMSE en tabla `prediccion_td` | ~0,54 pp |
| Filas en `fact_informalidad` | > 500 registros |
| Filas en `fact_demanda_sena` | ~566 registros |

## Demo en vivo (sin instalación)

La solución está desplegada y disponible sin necesidad de instalar nada:

**Web app:** https://economia-empleo.vercel.app

Las 5 secciones de la web app muestran los datos procesados con los mismos resultados que se obtienen al ejecutar el pipeline completo localmente.
