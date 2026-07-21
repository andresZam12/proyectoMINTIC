# Dashboard Predictivo del Mercado Laboral Colombiano

> **Concurso Datos al Ecosistema 2026: IA para Colombia — Reto 5: Economía y Empleo**
> **Equipo:** Andrés Zambrano · Daniers Solarte · Deivid Alvarado · Luna Mideros
> **Institución:** Ingeniería de Software — Universidad Cooperativa de Colombia (UCC)

---

## Descripción del proyecto

El **Dashboard Predictivo del Mercado Laboral Colombiano** es una solución de análisis de datos e inteligencia artificial desarrollada para integrar, procesar y visualizar información relacionada con el mercado laboral de Colombia.

El proyecto combina información proveniente de diferentes fuentes oficiales, principalmente **DANE, SENA y Ministerio del Trabajo**, con el objetivo de facilitar el análisis de indicadores como el desempleo, la ocupación, la participación laboral y la informalidad.

Además del análisis descriptivo, la solución incorpora un componente de **inteligencia artificial y análisis predictivo**, que permite estimar el comportamiento futuro de la tasa de desocupación nacional a partir del comportamiento histórico de los datos.

La información procesada se presenta mediante una aplicación web y un dashboard interactivo, permitiendo que usuarios como investigadores, estudiantes, ciudadanos y tomadores de decisiones puedan consultar los principales indicadores del mercado laboral de una manera más sencilla y centralizada.

---

## Problema abordado

La información relacionada con el mercado laboral colombiano se encuentra distribuida en múltiples fuentes oficiales y en diferentes formatos de publicación.

Por ejemplo, los boletines técnicos del **DANE** relacionados con la Gran Encuesta Integrada de Hogares (GEIH) se publican principalmente como documentos PDF mensuales. Por otro lado, las estadísticas relacionadas con la informalidad laboral se encuentran disponibles en archivos Excel con estructuras que pueden variar entre períodos, mientras que los datos relacionados con la demanda de formación y ocupaciones del **SENA** se encuentran disponibles en una fuente independiente.

Esta dispersión de información dificulta el análisis conjunto de los datos, ya que un usuario debe consultar diferentes páginas, descargar archivos y realizar procesos manuales para comparar los indicadores.

Actualmente, no existe un único punto de consulta que permita analizar de forma integrada:

* La evolución histórica de la tasa de desempleo.
* La tasa de ocupación y participación laboral.
* El comportamiento de la informalidad en diferentes ciudades.
* Las diferencias de informalidad según sexo.
* Las ocupaciones con mayor número de inscritos en programas de formación del SENA.
* Las tendencias futuras del desempleo en Colombia.

Por esta razón, el proyecto busca centralizar y procesar estas fuentes de información para construir una solución analítica que permita comprender mejor la situación del mercado laboral colombiano y apoyar la toma de decisiones basada en datos.

---

## Justificación

Colombia ha presentado históricamente niveles importantes de desempleo, acompañados de diferencias significativas entre regiones y ciudades. Además, el mercado laboral presenta comportamientos estacionales, donde las tasas de desempleo pueden aumentar o disminuir dependiendo del período del año.

La informalidad laboral también representa un desafío importante, ya que una parte considerable de la población ocupada desarrolla sus actividades laborales sin contar con todas las condiciones asociadas a un empleo formal.

En este contexto, el proyecto genera **valor público y empresarial** al integrar información de diferentes entidades oficiales en una única solución tecnológica.

La utilización de técnicas de análisis de datos e inteligencia artificial permite no solamente observar el comportamiento histórico del mercado laboral, sino también identificar tendencias y realizar predicciones que pueden servir como apoyo para la planificación de políticas públicas.

La solución puede contribuir a:

* Anticipar posibles períodos de aumento del desempleo.
* Identificar diferencias en los niveles de informalidad entre ciudades.
* Analizar brechas relacionadas con el género en el mercado laboral.
* Conocer las ocupaciones con mayor demanda de formación.
* Apoyar la planificación de programas de capacitación y formación profesional.
* Facilitar el acceso ciudadano a información laboral mediante visualizaciones sencillas e interactivas.

---

## Objetivos del proyecto

### Objetivo general

Desarrollar un dashboard predictivo que integre información de diferentes fuentes oficiales sobre el mercado laboral colombiano, permitiendo analizar indicadores de desempleo, ocupación e informalidad y generar predicciones sobre el comportamiento futuro de la tasa de desocupación.

### Objetivos específicos

1. Integrar datos provenientes de DANE, SENA y Ministerio del Trabajo.
2. Procesar y transformar datos publicados en diferentes formatos, como PDF, Excel y API.
3. Construir una base de datos estructurada para almacenar la información procesada.
4. Analizar el comportamiento histórico de los principales indicadores laborales.
5. Comparar los niveles de informalidad entre diferentes ciudades y grupos poblacionales.
6. Implementar un modelo predictivo para estimar la evolución futura de la tasa de desempleo.
7. Crear una aplicación web y un dashboard que permitan consultar los resultados de manera visual e interactiva.
8. Facilitar la reproducción y ejecución del proyecto mediante Docker.

---

## Datasets utilizados

**Cantidad de datasets principales:** 4

### Dataset proveniente de datos.gov.co *(obligatorio)*

| Dataset                      | Fuente                                                                      | Registros | Período   |
| ---------------------------- | --------------------------------------------------------------------------- | --------- | --------- |
| Inscritos SENA por ocupación | [datos.gov.co](https://www.datos.gov.co/Trabajo/Ocupaciones-SENA/8pqf-rmzr) | 566       | 2019–2020 |

Este dataset permite analizar la cantidad de personas inscritas en programas de formación relacionados con diferentes ocupaciones. Su integración permite complementar los indicadores del mercado laboral con información relacionada con la demanda de formación profesional.

### Datasets externos de portales oficiales

| Dataset                                      | Fuente                                                                                                             | Formato          | Período           |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ---------------- | ----------------- |
| Boletines técnicos GEIH (TD, TO, TGP)        | [DANE](https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-y-desempleo)                 | PDF mensual      | May 2023–Feb 2026 |
| Anexos EISS — Informalidad por ciudad y sexo | [DANE](https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-informal-y-seguridad-social) | Excel trimestral | 2021–2026         |
| Indicadores FILCO                            | [MinTrabajo](https://filco.mintrabajo.gov.co)                                                                      | Excel            | 2021–2026         |

Estos datasets permiten complementar la información y realizar análisis desde diferentes perspectivas. Mientras los datos de la GEIH permiten estudiar el desempleo y la ocupación, los datos de informalidad permiten realizar comparaciones territoriales y por sexo.

---

## Variables seleccionadas

| Variable                    | Descripción                                                                                    | Fuente    |
| --------------------------- | ---------------------------------------------------------------------------------------------- | --------- |
| `tasa_desocupacion`         | Porcentaje de la población económicamente activa que se encuentra desempleada                  | DANE GEIH |
| `tasa_ocupacion`            | Porcentaje de la población en edad de trabajar que se encuentra ocupada                        | DANE GEIH |
| `tasa_global_participacion` | Porcentaje de la población en edad de trabajar que participa activamente en el mercado laboral | DANE GEIH |
| `tasa_informalidad`         | Proporción de personas ocupadas que trabajan en condiciones de informalidad                    | DANE EISS |
| `variacion_anual_td`        | Cambio de la tasa de desempleo en puntos porcentuales respecto al mismo mes del año anterior   | Calculada |
| `inscritos`                 | Número de personas inscritas en programas de formación relacionados con una ocupación          | SENA      |
| `ciudad`                    | Ciudad o área geográfica donde se realiza la medición de informalidad                          | DANE EISS |
| `sexo`                      | Categoría utilizada para analizar las diferencias de informalidad entre hombres y mujeres      | DANE EISS |

Estas variables fueron seleccionadas debido a que permiten analizar diferentes dimensiones del mercado laboral colombiano y establecer relaciones entre el desempleo, la ocupación, la informalidad y la formación profesional.

---

## Proceso de análisis de datos

El proyecto sigue un flujo de procesamiento de datos compuesto por varias etapas:

1. **Extracción:** se recopila información desde las fuentes oficiales seleccionadas.
2. **Limpieza:** se corrigen inconsistencias, valores faltantes y diferencias en los formatos.
3. **Transformación:** los datos se convierten a estructuras estandarizadas para facilitar su análisis.
4. **Integración:** la información de las diferentes fuentes se combina en un modelo de datos estructurado.
5. **Almacenamiento:** los datos procesados se almacenan en PostgreSQL.
6. **Análisis:** se realizan análisis descriptivos y estadísticos sobre los indicadores laborales.
7. **Modelado predictivo:** se entrena un modelo de series temporales para predecir la tasa de desocupación.
8. **Visualización:** los resultados se presentan mediante una aplicación web y dashboards interactivos.

Este flujo permite automatizar gran parte del proceso y facilita la reproducción del proyecto desde cero.

---

## Tipo de análisis

El proyecto utiliza principalmente un enfoque **predictivo**, complementado con análisis descriptivo y estadístico.

### Análisis predictivo

Se realiza un **forecasting univariado de series temporales** utilizando como variable principal la tasa de desocupación mensual nacional.

El objetivo es analizar el comportamiento histórico del desempleo y utilizar esta información para estimar su posible comportamiento en períodos futuros.

### Análisis descriptivo

Se analiza la evolución de indicadores como:

* Tasa de desempleo.
* Tasa de ocupación.
* Tasa global de participación.
* Tasa de informalidad.
* Informalidad por ciudad.
* Informalidad por sexo.
* Inscritos por ocupación en programas del SENA.

### Análisis estadístico

Se utiliza un análisis **ANOVA de una vía** para comparar las tasas de informalidad entre diferentes ciudades y determinar si existen diferencias estadísticamente significativas entre los grupos analizados.

---

## Modelo utilizado

El modelo principal utilizado es **Holt-Winters**, basado en la técnica de suavización exponencial triple.

El modelo utiliza:

* **Tendencia aditiva**, para identificar el comportamiento general de la serie.
* **Estacionalidad aditiva**, considerando un período de 12 meses para representar posibles patrones anuales.

El sistema también incluye una lógica de detección automática de **Prophet**, desarrollado originalmente por Meta. Si esta biblioteca se encuentra disponible y configurada correctamente, el sistema puede utilizarla como primera alternativa. En caso contrario, se utiliza Holt-Winters como modelo de respaldo.

Para evaluar el desempeño del modelo se utiliza una división de los datos **80/20**, donde aproximadamente el 80 % de la información se utiliza para entrenar el modelo y el 20 % restante se reserva para evaluar sus predicciones.

En el conjunto disponible, esto corresponde aproximadamente a:

* **27 meses para entrenamiento.**
* **7 meses para prueba.**

---

## Resultados clave

| Métrica                                | Meta          | Resultado           |
| -------------------------------------- | ------------- | ------------------- |
| MAE (Error Absoluto Medio)             | ≤ 1,0 pp      | **0,43 pp** ✓       |
| RMSE (Raíz del Error Cuadrático Medio) | ≤ 1,5 pp      | **0,54 pp** ✓       |
| Cobertura histórica                    | Mínimo 2 años | May 2023–Feb 2026 ✓ |
| Fuentes integradas                     | Mínimo 3      | 4 fuentes ✓         |

Los resultados obtenidos muestran que el modelo presenta un desempeño adecuado para el objetivo planteado, ya que los errores de predicción se encuentran dentro de los valores establecidos como meta para el proyecto.

### Predicción H2 2026

De acuerdo con el modelo desarrollado, para el segundo semestre de 2026 se estima que la tasa de desocupación colombiana se mantendrá aproximadamente entre **6,5 % y 9,0 %**, considerando una banda de confianza aproximada de **±1,2 puntos porcentuales**.

> **Nota:** Esta predicción representa una estimación generada por el modelo a partir de los datos históricos disponibles y no debe interpretarse como un valor oficial publicado por el DANE.

---

## Interpretación de los resultados

El modelo logra capturar el comportamiento general de la tasa de desempleo colombiana durante el período analizado.

Se observa una tendencia de disminución del desempleo desde niveles cercanos al **11 % en 2023** hacia valores cercanos al **8 % durante 2025 y 2026**.

También se identifica un comportamiento estacional anual. De acuerdo con los datos analizados, la tasa de desempleo suele presentar incrementos durante los primeros meses del año, especialmente en enero y febrero, mientras que posteriormente tiende a disminuir durante otros períodos del año.

El resultado obtenido de **MAE = 0,43 puntos porcentuales** indica que, en promedio, las predicciones del modelo presentan un error absoluto relativamente bajo frente a los valores reales observados.

Por ejemplo, si el valor real de la tasa de desempleo fuera del **10,5 %**, un error aproximado de 0,43 puntos porcentuales significaría que la predicción podría encontrarse alrededor de ese valor, aunque el error real puede variar entre diferentes períodos.

---

## Impacto potencial

### Tomadores de decisiones

La solución proporciona una vista integrada del mercado laboral, reduciendo la necesidad de consultar manualmente diferentes boletines, archivos Excel y fuentes de datos.

La capacidad predictiva puede servir como herramienta de apoyo para anticipar posibles períodos de aumento del desempleo y facilitar la planificación de políticas públicas.

### Investigadores y analistas

El proyecto proporciona una base de datos estructurada en PostgreSQL y un flujo de procesamiento reproducible.

La arquitectura permite actualizar los datos y volver a ejecutar los procesos de transformación y modelado utilizando Docker.

### Instituciones educativas y de formación

Los datos relacionados con las ocupaciones e inscritos del SENA pueden utilizarse como referencia para analizar tendencias relacionadas con la formación profesional y las necesidades del mercado laboral.

### Ciudadanos y periodistas

La aplicación web permite consultar información sobre desempleo e informalidad mediante visualizaciones interactivas, sin necesidad de instalar herramientas especializadas ni tener conocimientos avanzados de análisis de datos.

---

## Solución en Producción (Demo en Vivo)

La solución cuenta con una aplicación web desplegada en producción y un video demostrativo donde se puede observar el funcionamiento general del proyecto.

**Video demo:** [Ver en YouTube](https://youtu.be/uf618RjgYhc)

**Aplicación Web / Producción:** [Visitar la solución en vivo](https://economia-empleo.vercel.app)

### Ejecución mediante Docker

El proyecto también puede ejecutarse localmente utilizando Docker:

```bash
git clone https://github.com/andresZam12/proyectoMINTIC.git
cd proyectoMINTIC/proyecto_mintic
docker-compose up -d
```

Al iniciar los contenedores, la base de datos se configura automáticamente.

Los servicios disponibles son:

* **Jupyter Lab:** `http://localhost:8888`
* **Token:** `mintic2026`
* **Adminer:** `http://localhost:8081`

Jupyter Lab permite ejecutar notebooks y procesos de análisis, mientras que Adminer proporciona una interfaz web para consultar y administrar la base de datos PostgreSQL.

---

## Stack tecnológico

| Capa            | Tecnología                             | Propósito                                                          |
| --------------- | -------------------------------------- | ------------------------------------------------------------------ |
| Extracción      | Python, Selenium, requests, pdfplumber | Obtención de datos desde fuentes oficiales                         |
| Transformación  | PySpark + JDBC                         | Procesamiento y transformación de grandes volúmenes de información |
| Base de datos   | PostgreSQL 15                          | Almacenamiento estructurado de los datos                           |
| Modelo IA       | Holt-Winters / Prophet                 | Predicción de la tasa de desempleo                                 |
| Web app         | Next.js + TypeScript                   | Desarrollo de la aplicación web                                    |
| Despliegue web  | Vercel                                 | Publicación de la aplicación en producción                         |
| Dashboard       | Power BI Desktop                       | Visualización y análisis interactivo                               |
| Infraestructura | Docker Compose                         | Configuración y ejecución de los servicios                         |

---

## Estructura del repositorio

```text
proyecto_mintic/
├── RECURSOS/                  # Material de presentación del proyecto
│   ├── presentacion.html      # Presentación interactiva
│   ├── presentacion.pdf       # Presentación en formato PDF
│   └── portada.png            # Imagen de portada
│
├── docs/                      # Documentación técnica detallada
│   ├── planteamiento_problema.md
│   ├── marco_metodologico.md
│   ├── fuentes_datos.md
│   ├── diccionario_datos.md
│   ├── architecture.md
│   ├── conclusiones.md
│   └── validation_guide.md
│
├── data/                      # Datos utilizados durante el proyecto
│   ├── 01_raw/                # Datos originales
│   ├── 02_intermediate/       # Datos semiprocesados
│   ├── 03_primary/            # Datos consolidados
│   └── 04_model_output/       # Resultados y predicciones del modelo
│
├── notebooks/                 # Notebooks de análisis exploratorio
│
├── pipelines/                 # Procesos automatizados de datos
│   ├── 01_datasource/         # Extracción de información
│   ├── 02_dataprocess/        # Limpieza, validación y parseo
│   ├── 03_datatransform/      # Transformación con PySpark y SQL
│   ├── 04_dataproduct/        # Construcción del modelo IA
│   └── pipeline_ml.py         # Orquestador del pipeline completo
│
├── src/                       # Módulos reutilizables
│   ├── config.py
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── model_training.py
│   ├── model_evaluation.py
│   └── pipeline_integration.py
│
├── models/                    # Modelos entrenados y serializados
├── reports/figures/           # Gráficas y resultados visuales
├── tests/                     # Pruebas de calidad de datos y modelos
├── pagina_web/                # Código fuente de la aplicación web
├── CRISP_ML.html              # Documentación metodológica CRISP-ML
├── docker-compose.yml         # Configuración de servicios Docker
├── requirements.txt           # Dependencias Python
└── README.md                  # Documentación principal
```

---

## Instalación y ejecución

Para ejecutar el proyecto localmente se deben seguir los siguientes pasos:

### 1. Clonar el repositorio

```bash
git clone https://github.com/andresZam12/proyectoMINTIC.git
cd proyectoMINTIC/proyecto_mintic
```

### 2. Instalar las dependencias de Python

```bash
pip install -r requirements.txt
```

### 3. Levantar los servicios Docker

```bash
docker-compose up -d
```

Este comando inicia los servicios necesarios para el funcionamiento del proyecto, incluyendo PostgreSQL, Jupyter Lab y Adminer.

### 4. Ejecutar el pipeline de datos

Los procesos de extracción, transformación y modelado deben ejecutarse en el orden correspondiente:

```bash
python pipelines/01_datasource/extraccion_sena.py
python pipelines/01_datasource/extraccion_dane_boletines.py
python pipelines/02_dataprocess/parsear_boletines.py
python pipelines/03_datatransform/transformar_informalidad.py
python pipelines/pipeline_ml.py
```

El pipeline permite automatizar el procesamiento de los datos hasta obtener los resultados necesarios para el análisis y la predicción.

Para consultar las instrucciones completas de reproducción y validación del proyecto, revisar el archivo:

`docs/validation_guide.md`

---

## Enlaces de acceso

* [Video demo (YouTube)](https://youtu.be/uf618RjgYhc)
* [Web app en producción](https://economia-empleo.vercel.app)
* [Presentación PDF](proyecto_mintic/RECURSOS/presentacion.pdf)
* [Presentación HTML interactiva](proyecto_mintic/RECURSOS/presentacion.html)
* [Documentación CRISP-ML](proyecto_mintic/CRISP_ML.html)

---

## Servicios Docker

| Servicio    | Puerto | Uso                                                        |
| ----------- | ------ | ---------------------------------------------------------- |
| PostgreSQL  | 5432   | Base de datos principal del proyecto                       |
| Jupyter Lab | 8888   | Ejecución de notebooks y procesos de análisis              |
| Adminer     | 8081   | Interfaz web para consultar y administrar la base de datos |

---

## Arquitectura general de la solución

El funcionamiento general del proyecto se puede resumir en el siguiente flujo:

**Fuentes oficiales → Extracción → Limpieza → Transformación → PostgreSQL → Análisis → Modelo predictivo → Dashboard y aplicación web**

La información se obtiene desde diferentes fuentes oficiales, posteriormente se procesa y estandariza para almacenarla en una base de datos estructurada. A partir de estos datos se realizan análisis descriptivos y estadísticos, además del entrenamiento del modelo predictivo.

Finalmente, los resultados obtenidos se presentan mediante herramientas de visualización y una aplicación web, permitiendo que los usuarios consulten la información de manera sencilla e interactiva.

---

## Conclusión

El **Dashboard Predictivo del Mercado Laboral Colombiano** integra técnicas de ingeniería de datos, análisis estadístico, inteligencia artificial y desarrollo web para abordar una problemática relacionada con la dispersión de información sobre el empleo en Colombia.

La integración de diferentes fuentes oficiales permite construir una visión más completa del mercado laboral, mientras que el modelo predictivo proporciona una herramienta adicional para analizar posibles tendencias futuras.

De esta manera, el proyecto demuestra cómo el uso de datos abiertos y tecnologías de inteligencia artificial puede contribuir al desarrollo de soluciones digitales orientadas al análisis y la toma de decisiones basada en evidencia.
