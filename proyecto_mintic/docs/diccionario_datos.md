# Diccionario de Datos

Todas las tablas residen en la base de datos `mintic_db` (PostgreSQL 15). El modelo sigue un **esquema estrella** con tablas de dimensiones y tablas de hechos.

---

## Tablas de dimensiones

### `dim_periodo`
Calendario mensual pre-poblado 2010–2026.

| Columna | Tipo | Descripción |
|---|---|---|
| `id_periodo` | SERIAL PK | Identificador único |
| `anio` | INT | Año (2010–2026) |
| `mes` | INT | Mes (1–12) |
| `trimestre` | INT | Trimestre calculado (1–4) |
| `fecha` | DATE | Primer día del mes |

### `dim_departamento`
23 departamentos colombianos + 7 áreas metropolitanas con códigos DANE.

| Columna | Tipo | Descripción |
|---|---|---|
| `id_departamento` | SERIAL PK | Identificador único |
| `codigo_dane` | CHAR(2) | Código oficial DANE (05, 08, 11…) |
| `nombre` | VARCHAR(100) | Nombre del departamento |
| `region` | VARCHAR(50) | Región geográfica (Caribe, Andina, etc.) |
| `es_area_metro` | BOOLEAN | True si es área metropolitana |

### `dim_ciudad`
27 ciudades principales con coordenadas para visualización en mapa.

| Columna | Tipo | Descripción |
|---|---|---|
| `id_ciudad` | SERIAL PK | Identificador único |
| `ciudad` | VARCHAR(120) UNIQUE | Nombre de la ciudad |
| `latitud` | NUMERIC(9,6) | Coordenada geográfica |
| `longitud` | NUMERIC(9,6) | Coordenada geográfica |
| `departamento` | VARCHAR(100) | Departamento al que pertenece |
| `region` | VARCHAR(50) | Región geográfica |

---

## Tablas de hechos

### `fact_mercado_laboral`
Indicadores laborales mensuales nacionales del DANE GEIH.

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | SERIAL PK | Identificador único |
| `id_periodo` | INT FK | Referencia a dim_periodo |
| `id_departamento` | INT FK | Referencia a dim_departamento |
| `sexo` | VARCHAR(10) | Total / Hombre / Mujer |
| `grupo_edad` | VARCHAR(20) | 15-28 / 29-45 / 46-65+ |
| `zona` | VARCHAR(20) | Cabecera / Resto |
| `nivel_educativo` | VARCHAR(50) | Sin educación / Primaria / Secundaria / Superior |
| `rama_actividad` | VARCHAR(100) | Sector económico |
| `posicion_ocupacional` | VARCHAR(100) | Tipo de empleo |
| `tasa_desocupacion` | NUMERIC(5,2) | Tasa de desempleo (%) |
| `tasa_ocupacion` | NUMERIC(5,2) | Tasa de ocupación (%) |
| `tasa_global_participacion` | NUMERIC(5,2) | TGP (%) |
| `tasa_formalidad` | NUMERIC(5,2) | % empleos formales |
| `tasa_informalidad` | NUMERIC(5,2) | % empleos informales |
| `variacion_anual_td` | NUMERIC(5,2) | Cambio vs. mismo mes año anterior (pp) |
| `fuente` | VARCHAR(20) | DANE / GEIH / FILCO |
| `fecha_carga` | TIMESTAMP | Fecha de inserción en BD |

### `fact_informalidad`
Tasas de informalidad por ciudad y sexo, fuente DANE EISS (trimestral).

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | SERIAL PK | Identificador único |
| `id_ciudad` | INT FK | Referencia a dim_ciudad |
| `id_periodo` | INT FK | Referencia a dim_periodo |
| `ocupados_total` | INT | Total de ocupados en la ciudad |
| `ocupados_formal` | INT | Ocupados en empleos formales |
| `ocupados_informal` | INT | Ocupados en empleos informales |
| `tasa_informalidad` | NUMERIC(5,2) | % informal sobre total ocupados |
| `sexo` | VARCHAR(10) | Total / Hombre / Mujer |
| `fecha_carga` | TIMESTAMP | Fecha de inserción en BD |

### `fact_demanda_sena`
Demanda de formación por ocupación, fuente API SENA datos.gov.co.

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | SERIAL PK | Identificador único |
| `id_periodo` | INT FK | Referencia a dim_periodo |
| `id_departamento` | INT FK | Referencia a dim_departamento |
| `ocupacion` | VARCHAR(200) | Nombre de la ocupación |
| `sector_economico` | VARCHAR(100) | Sector (comercio, servicios, etc.) |
| `inscritos` | INT | Número de inscritos |
| `vacantes` | INT | Vacantes disponibles (si aplica) |
| `fuente` | VARCHAR(20) | SENA |
| `fecha_carga` | TIMESTAMP | Fecha de inserción en BD |

### `prediccion_td`
Resultados del modelo Holt-Winters para los próximos 6 meses.

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | SERIAL PK | Identificador único |
| `fecha` | DATE | Mes predicho |
| `td_predicha` | NUMERIC(5,2) | Tasa de desocupación proyectada (%) |
| `td_lower` | NUMERIC(5,2) | Límite inferior intervalo de confianza 90% |
| `td_upper` | NUMERIC(5,2) | Límite superior intervalo de confianza 90% |
| `mae` | NUMERIC(5,4) | MAE del modelo en el período de prueba |
| `rmse` | NUMERIC(5,4) | RMSE del modelo en el período de prueba |
| `modelo` | VARCHAR(50) | Nombre del modelo usado (holt-winters / prophet) |
| `fecha_generado` | TIMESTAMP | Fecha en que se generó la predicción |
