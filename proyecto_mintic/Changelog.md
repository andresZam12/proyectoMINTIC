# Changelog

Todos los cambios relevantes del proyecto se documentan aquí siguiendo [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

---

## [1.3.0] — 2026-07-07

### Añadido
- Web app pública en Next.js desplegada en Vercel (`economia-empleo.vercel.app`)
- Sección ANOVA Estadístico para comparación de informalidad entre ciudades
- Estructura completa de repositorio nivel intermedio (notebooks, tests, pipelines, CI)
- Documentación `docs/` completa: 7 archivos markdown técnicos
- `environment.yml` para reproducción con conda
- GitHub Actions CI para validación automática de pruebas

### Modificado
- README.md reestructurado con ficha técnica completa del concurso
- CRISP_ML.html actualizado con sección de despliegue y ANOVA

---

## [1.2.0] — 2026-04-29

### Añadido
- Power BI dashboard completo: 4 páginas (Panorama Nacional, Tendencia, SENA, Predicción IA)
- `transformar_informalidad.py`: carga de datos EISS por ciudad y sexo a PostgreSQL
- `agregar_coordenadas.sql`: tabla `dim_ciudad` con coordenadas para mapas
- Documentación CRISP-ML completa (13 páginas)

### Modificado
- `modelo_prophet.py`: fallback automático a Holt-Winters si Prophet no compila
- `docker-compose.yml`: ajuste de credenciales y variables de entorno

---

## [1.1.0] — 2026-04-22

### Añadido
- `modelo_prophet.py`: modelo Holt-Winters con MAE=0,43pp y RMSE=0,54pp
- `prediccion_td.csv`: predicciones a 6 meses con intervalo de confianza
- `forecast_prophet.png`: visualización de la serie histórica + forecast
- `validar_datos.py`: inventario del data lake con hashes MD5 y porcentaje de nulos

### Corregido
- Encoding de columnas SENA (ñ → _n_): mapeo explícito en `transformar.py`
- Parser de trimestres cruzados en anexos EISS (offset de año en "Nov21-Ene22")

---

## [1.0.0] — 2026-04-15

### Añadido
- Pipeline ETL completo: extracción, procesamiento, transformación y carga a PostgreSQL
- `extraccion_sena.py`: descarga de 566 registros desde API datos.gov.co
- `extraccion_dane_boletines.py`: descarga de 34 boletines PDF del DANE
- `parsear_boletines.py`: extracción de TD, TO, TGP de los 34 PDFs (100% cobertura)
- `transformar.py`: carga con PySpark + JDBC a esquema estrella PostgreSQL
- `crear_tablas.sql`: DDL de las tablas del data warehouse
- `docker-compose.yml`: infraestructura con PostgreSQL 15, Jupyter PySpark y Adminer
- `requirements.txt` y `.gitignore`
