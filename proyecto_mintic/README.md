# Dashboard Predictivo del Mercado Laboral Colombiano

> **Concurso Datos al Ecosistema 2026: IA para Colombia — Reto 5: Economía y Empleo**
> Equipo: Andrés Zambrano · Daniers Solarte · Deivid Alvarado · Luna Mideros
> Institución: Ingeniería de Software — UCC

---

## Problema abordado

La información sobre el mercado laboral colombiano está dispersa en múltiples fuentes oficiales: los boletines del DANE son PDFs mensuales, las estadísticas de informalidad se publican en Excel con formatos distintos cada trimestre, y los datos de demanda de formación del SENA están en una API separada. No existe un punto de consulta integrado donde un tomador de decisiones pueda ver, en un solo lugar, cómo evoluciona el desempleo, qué tan informal es el trabajo en cada ciudad, qué ocupaciones demanda el mercado, y hacia dónde apunta la tendencia en los próximos meses.

## Justificación

Colombia tiene históricamente una de las tasas de desempleo más altas de América Latina, con marcada estacionalidad y diferencias regionales significativas. Esta solución genera valor público al integrar datos abiertos de DANE, SENA y MinTrabajo en un sistema analítico accesible desde cualquier navegador, permitiendo anticipar períodos críticos de desempleo con un modelo de IA y orientar políticas de formación profesional y formalización laboral basadas en evidencia.

---

## Datasets utilizados

**Cantidad de datasets:** 4

### Desde datos.gov.co *(obligatorio)*

| Dataset | Fuente | Registros | Período |
|---|---|---|---|
| [Inscritos SENA por ocupación](https://www.datos.gov.co/Trabajo/Ocupaciones-SENA/8pqf-rmzr) | datos.gov.co | 566 | 2019–2020 |

### Datasets externos (portales oficiales)

| Dataset | Fuente | Formato | Período |
|---|---|---|---|
| Boletines técnicos GEIH (TD, TO, TGP) | [DANE](https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo) | PDF mensual | May 2023–Feb 2026 |
| Anexos EISS — Informalidad por ciudad y sexo | [DANE](https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-informal-y-seguridad-social) | Excel trimestral | 2021–2026 |
| Indicadores FILCO | [MinTrabajo](https://filco.mintrabajo.gov.co) | Excel | 2021–2026 |

---

## Variables seleccionadas

| Variable | Descripción | Fuente |
|---|---|---|
| `tasa_desocupacion` | Tasa de desempleo mensual nacional (%) | DANE GEIH |
| `tasa_ocupacion` | Porcentaje de población en edad de trabajar que está ocupada (%) | DANE GEIH |
| `tasa_global_participacion` | Porcentaje de la población en edad de trabajar que participa en el mercado laboral (%) | DANE GEIH |
| `tasa_informalidad` | Proporción de ocupados en empleos informales por ciudad (%) | DANE EISS |
| `variacion_anual_td` | Cambio en puntos porcentuales respecto al mismo mes del año anterior | Calculada |
| `inscritos` | Número de personas inscritas en programas SENA por ocupación | SENA |
| `ciudad` | Ciudad de medición para indicadores de informalidad | DANE EISS |
| `sexo` | Desagregación por sexo de la tasa de informalidad | DANE EISS |

---

## Tipo de análisis

**Predictivo** — Forecasting univariado de series temporales sobre la tasa de desocupación mensual nacional, complementado con análisis descriptivo de informalidad laboral por ciudad y análisis estadístico ANOVA para comparación entre ciudades.

## Modelo utilizado

**Holt-Winters** (suavización exponencial triple) con tendencia aditiva y estacionalidad aditiva de período 12 meses. El script detecta automáticamente si **Prophet** (Meta/Facebook) está disponible y lo usa como primera opción; si no, usa Holt-Winters como fallback. Evaluación con hold-out 80/20 (27 meses entrenamiento / 7 meses prueba). Análisis complementario: **ANOVA de una vía** sobre tasas de informalidad por ciudad.

---

## Resultados clave

| Métrica | Meta | Resultado |
|---|---|---|
| MAE (Error Absoluto Medio) | ≤ 1,0 pp | **0,43 pp** ✓ |
| RMSE (Raíz del Error Cuadrático Medio) | ≤ 1,5 pp | **0,54 pp** ✓ |
| Cobertura histórica | Mínimo 2 años | May 2023–Feb 2026 ✓ |
| Fuentes integradas | Mínimo 3 | 4 fuentes ✓ |

**Predicción H2 2026:** la tasa de desocupación colombiana se mantendrá entre **6,5 % y 9,0 %** con una banda de confianza de ±1,2 pp.

## Interpretación

El modelo captura correctamente la tendencia bajista del desempleo colombiano desde 2023 (~11%) hasta 2025-2026 (~8%), así como la estacionalidad anual: el desempleo sube en enero-febrero y baja en el segundo semestre. Un MAE de 0,43 pp significa que si la tasa real es 10,5%, el modelo predice entre 10,07% y 10,93%, margen aceptable para un indicador macroeconómico mensual.

## Impacto potencial

- **Tomadores de decisión:** vista integrada del mercado laboral sin cruzar manualmente boletines, Excel y microdatos. La predicción a 6 meses permite anticipar períodos críticos y preparar políticas con anticipación.
- **Investigadores:** base de datos estructurada en PostgreSQL con esquema estrella, reproducible desde cero con Docker.
- **Ciudadanos y periodistas:** web app pública sin instalación ni conocimientos técnicos, con visualizaciones interactivas de desempleo e informalidad por ciudad.

---

## Solución en Producción (Demo en Vivo)

Para ver y probar la solución funcionando en tiempo real:

**Video demo:** [Ver en YouTube](https://youtu.be/uf618RjgYhc)

**Aplicación Web / Producción:** [Visitar la solución en vivo](https://economia-empleo.vercel.app)

**Contenedor listo (Docker):**
```bash
git clone https://github.com/andresZam12/proyectoMINTIC.git
cd proyectoMINTIC/proyecto_mintic
docker-compose up -d
```

La base de datos se inicializa automáticamente. Jupyter Lab disponible en `http://localhost:8888` (token: `mintic2026`). Adminer en `http://localhost:8081`.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Extracción | Python, Selenium, requests, pdfplumber |
| Transformación | PySpark + JDBC |
| Base de datos | PostgreSQL 15 (Docker) |
| Modelo IA | Holt-Winters / Prophet (statsmodels / Prophet) |
| Web app | Next.js + TypeScript (Vercel) |
| Dashboard | Power BI Desktop |
| Infraestructura | Docker Compose |

---

## Estructura del repositorio

```
proyecto_mintic/
├── RECURSOS/                  # Presentación del proyecto
│   ├── presentacion.html
│   ├── presentacion.pdf
│   └── portada.png
├── docs/                      # Documentación técnica detallada
│   ├── planteamiento_problema.md
│   ├── marco_metodologico.md
│   ├── fuentes_datos.md
│   ├── diccionario_datos.md
│   ├── architecture.md
│   ├── conclusiones.md
│   └── validation_guide.md
├── data/
│   ├── 01_raw/                # Datos originales (.gitignore — solo .gitkeep)
│   ├── 02_intermediate/       # Datos semiprocesados
│   ├── 03_primary/            # Serie temporal consolidada
│   └── 04_model_output/       # Predicciones del modelo
├── notebooks/                 # Análisis exploratorio y modelado
├── pipelines/
│   ├── 01_datasource/         # Scripts de extracción
│   ├── 02_dataprocess/        # Validación y parseo
│   ├── 03_datatransform/      # PySpark + DDL SQL
│   ├── 04_dataproduct/        # Modelo IA
│   └── pipeline_ml.py         # Orquestador completo
├── src/                       # Módulos de librería reutilizables
│   ├── config.py
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── model_training.py
│   ├── model_evaluation.py
│   └── pipeline_integration.py
├── models/                    # Modelos serializados (.pkl)
├── reports/figures/           # Gráficas generadas
├── tests/                     # Tests de calidad de datos y modelo
├── pagina_web/                # Código fuente web app (Next.js)
├── CRISP_ML.html              # Documentación metodológica CRISP-ML
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/andresZam12/proyectoMINTIC.git
cd proyectoMINTIC/proyecto_mintic

# 2. Instalar dependencias Python
pip install -r requirements.txt

# 3. Levantar contenedores (PostgreSQL + Jupyter + Adminer)
docker-compose up -d

# 4. Ejecutar pipeline completo (en orden)
python pipelines/01_datasource/extraccion_sena.py
python pipelines/01_datasource/extraccion_dane_boletines.py
python pipelines/02_dataprocess/parsear_boletines.py
python pipelines/03_datatransform/transformar_informalidad.py
python pipelines/pipeline_ml.py
```

Ver [`docs/validation_guide.md`](docs/validation_guide.md) para instrucciones detalladas de reproducción.

---

## Enlaces de acceso

- [Video demo (YouTube)](https://youtu.be/uf618RjgYhc)
- [Web app en producción](https://economia-empleo.vercel.app)
- [Presentación PDF](RECURSOS/presentacion.pdf)
- [Presentación HTML interactiva](RECURSOS/presentacion.html)
- [Documentación CRISP-ML](CRISP_ML.html)

---

## Servicios Docker

| Servicio | Puerto | Uso |
|---|---|---|
| PostgreSQL | 5432 | Base de datos principal |
| Jupyter Lab | 8888 | Ejecutar PySpark (token: mintic2026) |
| Adminer | 8081 | Interfaz web para consultar la BD |
