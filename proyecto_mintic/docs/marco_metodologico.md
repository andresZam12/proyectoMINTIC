# Marco Metodológico — CRISP-ML(Q)

## Metodología adoptada

El proyecto sigue **CRISP-ML(Q)** (Cross-Industry Standard Process for Machine Learning with Quality assurance), una adaptación del clásico CRISP-DM orientada a proyectos de machine learning. A diferencia de CRISP-DM, CRISP-ML incorpora criterios de calidad explícitos en cada fase y reconoce que el ciclo de vida de un proyecto de IA no termina con el modelo: también incluye despliegue, monitoreo y actualización continua.

---

## Fases del proceso

### Fase 1 — Comprensión del problema
Definición del tipo de problema ML (forecasting univariado), establecimiento de criterios de éxito medibles (MAE ≤ 1,0 pp, RMSE ≤ 1,5 pp) y mapeo de las partes interesadas (tomadores de decisión, investigadores, ciudadanos).

### Fase 2 — Comprensión de los datos
Exploración de cada fuente por separado antes de integrarlas. Identificación de problemas de calidad: PDFs con formatos variables, Excel con encabezados en dos filas, columnas con encoding especial en el CSV del SENA. Documentación de todos los problemas encontrados en `metadata.json`.

### Fase 3 — Preparación de los datos
Pipeline ETL de cuatro etapas:
```
F1 DataSource → F2 DataProcess → F3 DataTransform → F4 DataProduct
```
- **Extracción:** Python con requests, Selenium y pdfplumber
- **Validación:** `validar_datos.py` genera inventario con hashes MD5 y porcentaje de nulos
- **Parseo:** `parsear_boletines.py` extrae tasas de 34 PDFs con dos estrategias (regex + tablas)
- **Transformación:** PySpark con JDBC hacia PostgreSQL 15 en esquema estrella

### Fase 4 — Modelado
Selección de **Holt-Winters** (suavización exponencial triple) por:
- Serie con solo 34 puntos (deep learning no aplica con este volumen)
- Tendencia y estacionalidad aditivas bien definidas
- Sin dependencias de compilación (reproducible en cualquier entorno)
- Prophet como opción prioritaria si el compilador Stan está disponible

Análisis complementario: **ANOVA de una vía** para validar que las diferencias de informalidad entre ciudades son estadísticamente significativas (no solo variación aleatoria).

### Fase 5 — Evaluación
- Estrategia hold-out 80/20 (27 meses entrenamiento / 7 meses prueba)
- MAE final: **0,43 pp** | RMSE final: **0,54 pp**
- Intervalo de confianza del 90%: ±1,645 desviaciones estándar del forecast

### Fase 6 — Despliegue y monitoreo
- Backend: tres contenedores Docker (PostgreSQL, Jupyter PySpark, Adminer)
- Frontend: web app Next.js desplegada en Vercel (`economia-empleo.vercel.app`)
- Actualización: mensual, al publicarse el nuevo boletín GEIH del DANE (~día 30 del mes siguiente)
- Reentrenamiento: no necesario desde cero; Holt-Winters es incremental por naturaleza

---

## Justificación de decisiones técnicas clave

| Decisión | Alternativa descartada | Razón |
|---|---|---|
| Holt-Winters | Prophet | Prophet requiere compilar Stan (CmdStan), falla en Windows sin MinGW |
| PySpark + JDBC | pandas directo | Escalabilidad y preparación para microdatos GEIH (millones de filas) |
| Esquema estrella PostgreSQL | CSV planos | Permite consultas eficientes desde Power BI y la web app sin joins costosos |
| Hold-out simple | Validación cruzada deslizante | Con 34 puntos, múltiples folds consumen demasiados datos de entrenamiento |
| Next.js en Vercel | Solo Power BI | Power BI requiere instalación local; la web app es accesible desde cualquier navegador |
