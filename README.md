# Proyecto MinTIC — Análisis del Mercado Laboral en Colombia

Proyecto de análisis de datos del mercado laboral colombiano desarrollado para el concurso MinTIC. Integra fuentes del DANE, SENA y MinTrabajo, procesa los datos con PySpark, los almacena en PostgreSQL y genera predicciones con un modelo de inteligencia artificial, todo visualizado en un dashboard de Power BI.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Extracción | Python, Selenium, requests |
| Procesamiento | pandas, pdfplumber |
| Transformación | PySpark + JDBC |
| Base de datos | PostgreSQL 15 (Docker) |
| Modelo IA | Prophet / Holt-Winters (statsmodels) |
| Visualización | Power BI Desktop |
| Infraestructura | Docker Compose |

---

## Requisitos previos

- Python 3.11+
- Docker Desktop
- Power BI Desktop (para abrir el dashboard)
- Google Chrome + ChromeDriver (para los scripts de Selenium)

---

## Instalación

```bash
# 1. Instalar dependencias de Python
pip install -r requirements.txt

# 2. Configurar variables de entorno
# Crear un archivo .env con las credenciales (ver sección abajo)

# 3. Levantar los contenedores (PostgreSQL + Jupyter + Adminer)
docker-compose up -d
```

El archivo `.env` debe tener:
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mintic_db
POSTGRES_USER=mintic_user
POSTGRES_PASSWORD=mintic2026
```

---

## Orden de ejecución

Ejecutar los scripts en este orden desde la carpeta `proyecto_mintic/`:

### Paso 1 — Extracción de datos
```bash
python src/1_datasource/extraccion_sena.py
python src/1_datasource/extraccion_dane_boletines.py
python src/1_datasource/extraccion_geih.py      # requiere Chrome
python src/1_datasource/extraccion_filco.py     # requiere Chrome
```

> Los datos GEIH y FILCO también se pueden descargar manualmente si el portal bloquea el scraping. Cada script muestra las instrucciones al final.

### Paso 2 — Procesamiento
```bash
python src/2_dataprocess/validar_datos.py       # valida integridad del Data Lake
python src/2_dataprocess/parsear_boletines.py   # extrae tasas de los PDFs del DANE
```

### Paso 3 — Transformación y carga a PostgreSQL
```bash
# Crear tablas (solo la primera vez)
psql -h localhost -U mintic_user -d mintic_db -f src/3_datatransform/ddl/crear_tablas.sql

# Cargar datos con PySpark (ejecutar dentro del contenedor Jupyter)
spark-submit src/3_datatransform/transformar.py

# Cargar datos de informalidad (se puede ejecutar localmente)
python src/3_datatransform/transformar_informalidad.py
```

### Paso 4 — Modelo de predicción
```bash
python src/4_dataproduct/modelo_prophet.py
```

Genera las predicciones para los próximos 6 meses y las guarda en la tabla `prediccion_td`.

---

## Estructura del proyecto

```
proyecto_mintic/
├── data/
│   ├── raw/                  # Datos originales descargados
│   │   ├── sena/
│   │   ├── dane_boletines/
│   │   ├── filco/
│   │   └── geih/
│   └── processed/            # Archivos generados por el pipeline
├── src/
│   ├── 1_datasource/         # Scripts de extracción
│   ├── 2_dataprocess/        # Validación y parseo
│   ├── 3_datatransform/      # Transformación con PySpark + DDL SQL
│   └── 4_dataproduct/        # Modelo IA
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Fuentes de datos

| Fuente | Descripción |
|---|---|
| **DANE — Boletines GEIH** | Tasas de desempleo, ocupación y participación laboral mensual (2023–2026) |
| **DANE — Anexos EISS** | Informalidad laboral por ciudad y sexo (2021–2026) |
| **SENA** | Inscritos por ocupación (2019–2020), vía API datos.gov.co |
| **FILCO / MinTrabajo** | Indicadores de formalidad laboral |

---

## Dashboard Power BI

El archivo `.pbix` se conecta directamente a PostgreSQL. Para abrirlo:

1. Abrir `dashboard_mintic.pbix` en Power BI Desktop
2. Ir a **Inicio → Transformar datos → Configuración del origen de datos**
3. Actualizar con tu servidor PostgreSQL (localhost:5432)
4. Hacer clic en **Actualizar**

El dashboard tiene 4 páginas:
- **Página 1** — Resumen nacional (KPIs principales)
- **Página 2** — Evolución temporal de las tasas
- **Página 3** — Informalidad por ciudad y sexo
- **Página 4** — Predicción IA + métricas del modelo

---

## Modelo de IA

El script intenta usar **Prophet** (Facebook) primero. Si no está disponible (requiere compilador C++ y Stan), usa automáticamente **Holt-Winters** de statsmodels, que funciona en cualquier entorno.

Métricas obtenidas con la serie histórica 2023–2026:
- **MAE = 0.43 pp** (error promedio de ±0.43 puntos porcentuales)
- **RMSE = 0.54 pp**

---

## Servicios Docker

| Servicio | Puerto | Uso |
|---|---|---|
| PostgreSQL | 5432 | Base de datos principal |
| Jupyter Lab | 8888 | Ejecutar PySpark |
| Adminer | 8081 | Interfaz web para consultar la BD |
