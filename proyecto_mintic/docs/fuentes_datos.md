# Fuentes de Datos

## Resumen

| # | Fuente | Tipo | Período | Registros | Disponibilidad |
|---|---|---|---|---|---|
| 1 | SENA — Inscritos por ocupación | API JSON (datos.gov.co) | 2019–2020 | 566 | Abierta, sin autenticación |
| 2 | DANE — Boletines técnicos GEIH | PDF mensual | May 2023–Feb 2026 | 34 archivos | Descarga directa dane.gov.co |
| 3 | DANE — Anexos EISS (informalidad) | Excel trimestral | 2021–2026 | ~3.200 registros | Portal FILCO MinTrabajo |
| 4 | DANE — Microdatos GEIH | ZIP/SAV por módulos | 2024–2025 | Millones de filas | Descarga con registro previo |

---

## Fuente 1 — SENA: Inscritos por ocupación

- **URL:** https://www.datos.gov.co/Trabajo/Ocupaciones-SENA/8pqf-rmzr
- **API endpoint:** `https://www.datos.gov.co/resource/8pqf-rmzr.json`
- **Script de extracción:** `src/1_datasource/extraccion_sena.py`
- **Archivo resultante:** `data/raw/sena/sena_inscritos.csv`
- **Método:** paginación Socrata en lotes de 10.000 registros, 3 reintentos automáticos
- **Columnas principales:** `nombre_de_la_ocupaci_n`, `n_mero_de_inscritos_2019`, `n_mero_de_inscritos_2020`
- **Nota:** las columnas con ñ vienen codificadas como secuencia de caracteres especiales; el mapeo correcto está en `transformar.py`

## Fuente 2 — DANE: Boletines técnicos GEIH

- **URL base:** https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo
- **Script de extracción:** `src/1_datasource/extraccion_dane_boletines.py`
- **Archivo resultante:** `data/raw/dane_boletines/` (34 PDFs, ~20 MB)
- **Script de parseo:** `src/2_dataprocess/parsear_boletines.py`
- **Archivo procesado:** `data/processed/serie_temporal_td.csv`
- **Estrategia de extracción:** dos estrategias complementarias — regex sobre texto corrido y búsqueda en tablas de las primeras 5 páginas
- **Variables extraídas:** `tasa_desocupacion`, `tasa_ocupacion`, `tasa_global_participacion`, `variacion_anual_td`
- **Validación:** rangos TD 5–25%, TO 45–70%, TGP 55–80%

## Fuente 3 — DANE: Anexos EISS (informalidad por ciudad)

- **URL:** https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-informal-y-seguridad-social
- **Portal:** FILCO — https://filco.mintrabajo.gov.co
- **Script de extracción:** `src/1_datasource/extraccion_filco.py`
- **Archivo resultante:** `data/raw/filco/` (~36 MB en archivos Excel)
- **Script de transformación:** `src/3_datatransform/transformar_informalidad.py`
- **Problema conocido:** encabezados en dos filas, celdas combinadas por año, trimestres móviles que cruzan años (ej. "Nov21-Ene22" → el enero pertenece al año 22, no al 21)
- **Ciudades cubiertas:** 23 ciudades principales + agregados nacionales

## Fuente 4 — DANE: Microdatos GEIH

- **URL:** https://microdatos.dane.gov.co/index.php/catalog
- **Script de extracción:** `src/1_datasource/extraccion_geih.py`
- **Nota:** requiere registro previo en el portal y descarga manual si el scraping es bloqueado. Los módulos descargados (cuando disponibles) se procesan en `transformar.py` con PySpark
- **Estado actual:** carpetas `data/raw/geih/2024/` y `data/raw/geih/2025/` pendientes de descarga manual

---

## Proceso de validación de calidad

El script `src/2_dataprocess/validar_datos.py` genera `data/raw/metadata.json` con:
- Inventario completo de archivos (nombre, tamaño, hash MD5)
- Porcentaje de nulos por columna en CSV/Excel
- Estado de cada fuente: OK / ADVERTENCIA / PARCIAL / PENDIENTE / ERROR
- Flag `listo_para_f3` que indica si se puede proceder a transformación
