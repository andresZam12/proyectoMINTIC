# Proyecto MinTIC 2026 — Contexto para Claude en VS Code

## ¿Qué es este proyecto?
Dashboard predictivo del mercado laboral colombiano.
Tiene doble propósito:
1. Concurso nacional "Datos al Ecosistema 2026 · IA para Colombia" (MinTIC)
2. Trabajo final de la materia "Herramientas Computacionales para la 
   Interpretación de Resultados" — 6.º semestre Ingeniería de Software

## Objetivo general
Desarrollar un dashboard interactivo en Power BI respaldado por un pipeline
de datos con PySpark y PostgreSQL, que integre datos abiertos del mercado
laboral colombiano (GEIH, FILCO, SENA) para analizar tendencias de empleo,
identificar sectores emergentes y predecir la tasa de desocupación nacional
mediante inteligencia artificial.

## Equipo
- Andrés  → Arquitectura, PySpark, Modelo IA, Documentación
- Daniers → Validación datos, Power BI páginas 1 y 3, SQL
- Deivid  → Scripts extracción, Power BI páginas 2 y 4, GitHub

## Stack tecnológico
- Python 3.13
- requests, Scrapy, Selenium (extracción)
- pandas, openpyxl (validación)
- PySpark + Jupyter via Docker (transformación)
- PostgreSQL 15 via Docker (almacenamiento)
- Prophet + scikit-learn (modelo IA)
- Power BI Desktop (dashboard final)
- Docker Desktop en Windows 11
- VS Code + extensión Claude

## Pipeline (4 etapas)
1. DataSource     → src/1_datasource/      Scripts de extracción
2. DataProcess    → src/2_dataprocess/     Validación del Data Lake
3. DataTransform  → src/3_datatransform/   PySpark + carga a PostgreSQL
4. DataProduct    → src/4_dataproduct/     Modelo Prophet + Power BI

## Estructura de carpetas
proyecto_mintic/
├── data/
│   ├── raw/
│   │   ├── geih/               ← Microdatos GEIH 2024/2025
│   │   ├── filco/              ← Indicadores FILCO MinTrabajo
│   │   ├── sena/               ← Inscritos Agencia Pública Empleo
│   │   └── dane_boletines/     ← Boletines PDF mensuales DANE
│   └── processed/              ← Parquet limpios post-PySpark
├── src/
│   ├── 1_datasource/
│   ├── 2_dataprocess/
│   ├── 3_datatransform/
│   │   └── ddl/
│   └── 4_dataproduct/
├── .env
├── docker-compose.yml
├── requirements.txt
├── CONTEXTO.md                 ← este archivo
└── README.md

## Tablas en PostgreSQL (mintic_db)
- dim_departamento       → catálogo 23 departamentos
- dim_periodo            → calendario mes-año 2010-2026
- fact_mercado_laboral   → tabla principal (GEIH + FILCO + DANE)
- fact_demanda_sena      → inscritos y vacantes SENA
- prediccion_td          → forecast 6 meses Prophet

## Credenciales Docker (localhost)
- PostgreSQL → puerto 5432  | DB: mintic_db | user: mintic_user | pass: mintic2026
- Jupyter    → puerto 8888  | token: mintic2026

## Fuentes de datos
| Fuente          | URL                                          | Estado     |
|-----------------|----------------------------------------------|------------|
| SENA APE        | datos.gov.co/resource/8pqf-rmzr.json         | ✅ Listo   |
| Boletines DANE  | dane.gov.co/files/operaciones/GEIH/          | ✅ Listo   |
| GEIH 2024       | microdatos.dane.gov.co/index.php/catalog/819 | ⬜ Pendiente|
| GEIH 2025       | microdatos.dane.gov.co/index.php/catalog/853 | ⬜ Pendiente|
| FILCO           | filco.mintrabajo.gov.co                      | ⬜ Pendiente|

## Estado actual del código
### Completado ✅
- docker-compose.yml → PostgreSQL + Jupyter corriendo
- src/1_datasource/extraccion_sena.py → 566 registros, 9 columnas
- src/1_datasource/extraccion_dane_boletines.py → 34 PDFs (may2023-feb2026)

### Pendiente ⬜
- src/1_datasource/extraccion_geih.py → Selenium (siguiente paso)
- src/1_datasource/extraccion_filco.py → descarga manual/Selenium
- src/2_dataprocess/validar_datos.py
- src/3_datatransform/transformar.ipynb (PySpark)
- src/3_datatransform/ddl/crear_tablas.sql
- src/4_dataproduct/modelo_prophet.py
- Conexión Power BI → PostgreSQL
- Dashboard 4 páginas

## Variables del proyecto (20 funcionales)
### GEIH (12): tasa_desocupacion, tasa_ocupacion, tasa_global_participacion,
### rama_actividad, posicion_ocupacional, ingreso_laboral, nivel_educativo,
### sexo, grupo_edad, zona, departamento, periodo
### FILCO (3): tasa_formalidad, tasa_informalidad, afiliacion_seg_social
### SENA (2): inscritos_por_depto, vacantes_por_oficio
### Calculadas (3): variacion_anual_TD, brecha_genero_empleo, prediccion_TD_6meses

## Reglas de código (seguir siempre)
- Funciones pequeñas, una sola responsabilidad cada una
- Constantes en MAYÚSCULAS al inicio del archivo
- try/except con reintentos en TODAS las llamadas de red
- Rutas siempre con os.path.join(), nunca hardcodeadas
- Comentarios explicando el POR QUÉ, no el QUÉ obvio
- Credenciales solo desde .env, nunca en el código
- data/raw/ es INMUTABLE — nunca se modifica
- Código en español (variables, funciones, comentarios)

## Dashboard Power BI — 4 páginas
- Página 1: Panorama Nacional → KPIs + mapa coroplético (Daniers)
- Página 2: Sectores y Empleo → barras + treemap + SENA (Deivid)
- Página 3: Brechas Laborales → género + edad + formalidad (Daniers)
- Página 4: Predicción IA     → Prophet forecast 6 meses (Andrés)

## Criterios de evaluación concurso (100 pts)
- Uso datos abiertos: 20 pts
- Uso de IA: 20 pts
- Impacto y escalabilidad: 20 pts
- Rigor técnico: 15 pts
- Innovación: 15 pts
- Diseño y usabilidad: 10 pts

## Fecha límite: 30 de abril de 2026