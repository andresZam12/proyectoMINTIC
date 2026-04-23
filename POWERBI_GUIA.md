# Guía Power BI — Dashboard Mercado Laboral Colombia

## 1. Conexión a PostgreSQL

1. Power BI Desktop → **Obtener datos** → **Base de datos PostgreSQL**
2. Servidor: `localhost`  Puerto: `5432`
3. Base de datos: `mintic_db`
4. Usuario: `mintic_user`  Contraseña: `mintic2026`
5. Importar (no DirectQuery) — los datos son pequeños

Tablas a importar:
- `dim_periodo`
- `dim_departamento`
- `fact_mercado_laboral`
- `fact_demanda_sena`
- `prediccion_td`

---

## 2. Relaciones (Model View)

```
dim_periodo[id_periodo]        →  fact_mercado_laboral[id_periodo]   (1:*)
dim_periodo[id_periodo]        →  fact_demanda_sena[id_periodo]       (1:*)
dim_departamento[id_depart.]   →  fact_mercado_laboral[id_depart.]   (1:*)
dim_departamento[id_depart.]   →  fact_demanda_sena[id_depart.]      (1:*)
```

**Nota:** `prediccion_td` NO tiene relación — se usa directamente en la Página 4.

---

## 3. Columna calculada en dim_periodo

En Power BI, agregar en `dim_periodo`:

```dax
Periodo Etiqueta = 
    FORMAT([fecha_inicio], "MMM YYYY", "es-CO")
```

---

## 4. Medidas DAX

### Tabla de medidas: `_Medidas`

Crear una tabla vacía llamada `_Medidas` (Enter Data → tabla en blanco) y agregar:

---

#### Página 1 — Panorama Nacional

```dax
TD Ultima =
    CALCULATE(
        LASTNONBLANKVALUE(
            dim_periodo[fecha_inicio],
            MAX(fact_mercado_laboral[tasa_desocupacion])
        ),
        ALLEXCEPT(fact_mercado_laboral, fact_mercado_laboral[fuente])
    )

TO Ultima =
    CALCULATE(
        LASTNONBLANKVALUE(
            dim_periodo[fecha_inicio],
            MAX(fact_mercado_laboral[tasa_ocupacion])
        )
    )

TGP Ultima =
    CALCULATE(
        LASTNONBLANKVALUE(
            dim_periodo[fecha_inicio],
            MAX(fact_mercado_laboral[tasa_global_participacion])
        )
    )

Variacion Anual TD =
    CALCULATE(
        LASTNONBLANKVALUE(
            dim_periodo[fecha_inicio],
            MAX(fact_mercado_laboral[variacion_anual_td])
        )
    )

TD Promedio Periodo =
    AVERAGE(fact_mercado_laboral[tasa_desocupacion])

TD Minima =
    MIN(fact_mercado_laboral[tasa_desocupacion])

TD Maxima =
    MAX(fact_mercado_laboral[tasa_desocupacion])
```

---

#### Página 2 — Sectores y Empleo (SENA)

```dax
Total Inscritos =
    SUM(fact_demanda_sena[inscritos])

Total Inscritos 2019 =
    CALCULATE(
        SUM(fact_demanda_sena[inscritos]),
        dim_periodo[anio] = 2019
    )

Total Inscritos 2020 =
    CALCULATE(
        SUM(fact_demanda_sena[inscritos]),
        dim_periodo[anio] = 2020
    )

Variacion Inscritos % =
    DIVIDE(
        [Total Inscritos 2020] - [Total Inscritos 2019],
        [Total Inscritos 2019],
        0
    )

Ranking Ocupacion =
    RANKX(
        ALL(fact_demanda_sena[ocupacion]),
        [Total Inscritos],,
        DESC
    )
```

---

#### Página 3 — Brechas Laborales

```dax
Brecha TD vs Promedio =
    [TD Ultima] - [TD Promedio Periodo]

TD Tendencia =
    VAR UltimosMeses =
        TOPN(
            6,
            SUMMARIZE(
                fact_mercado_laboral,
                dim_periodo[fecha_inicio],
                "TD", MAX(fact_mercado_laboral[tasa_desocupacion])
            ),
            [fecha_inicio],
            DESC
        )
    RETURN
        AVERAGEX(UltimosMeses, [TD])

Alerta TD Alta =
    IF([TD Ultima] > 11, "Alto", IF([TD Ultima] > 9, "Medio", "Normal"))
```

---

#### Página 4 — Predicción IA

```dax
-- Medida de la última TD observada (para empalmar con forecast)
TD Historica Ultimo =
    CALCULATE(
        MAX(fact_mercado_laboral[tasa_desocupacion]),
        TOPN(
            1,
            SUMMARIZE(
                fact_mercado_laboral,
                dim_periodo[fecha_inicio],
                "TD", MAX(fact_mercado_laboral[tasa_desocupacion])
            ),
            [fecha_inicio],
            DESC
        )
    )

-- En prediccion_td directamente:
Pred TD Promedio = AVERAGE(prediccion_td[td_predicha])

Pred Intervalo Ancho =
    AVERAGE(prediccion_td[td_upper]) - AVERAGE(prediccion_td[td_lower])

MAE Modelo = FIRSTNONBLANK(prediccion_td[mae], 1)

RMSE Modelo = FIRSTNONBLANK(prediccion_td[rmse], 1)

Nombre Modelo = FIRSTNONBLANK(prediccion_td[modelo], 1)
```

---

## 5. Layout por página

### Página 1: Panorama Nacional

| Visual | Datos | Configuración |
|--------|-------|---------------|
| Tarjeta | `[TD Ultima]` | Formato: `0.0"%"` · Etiqueta: "Tasa de Desocupación (Feb 2026)" |
| Tarjeta | `[TO Ultima]` | Etiqueta: "Tasa de Ocupación" |
| Tarjeta | `[TGP Ultima]` | Etiqueta: "T. Global Participación" |
| Tarjeta | `[Variacion Anual TD]` | Color condicional: rojo si > 0 |
| Gráfico de líneas | Eje X: `dim_periodo[Periodo Etiqueta]` · Eje Y: `[TD Promedio Periodo]`, `[TO Ultima]`, `[TGP Ultima]` | Ordenar por `fecha_inicio` |
| Segmentador | `dim_periodo[anio]` | Selección múltiple |

---

### Página 2: Sectores y Empleo

| Visual | Datos | Configuración |
|--------|-------|---------------|
| Tarjeta | `[Total Inscritos 2019]` | |
| Tarjeta | `[Total Inscritos 2020]` | |
| Tarjeta | `[Variacion Inscritos %]` | Formato: `+0.0%` |
| Gráfico barras horizontal | Eje Y: `fact_demanda_sena[ocupacion]` · Eje X: `[Total Inscritos]` · Filtro: `[Ranking Ocupacion] <= 15` | Top 15 ocupaciones |
| Gráfico columnas agrupadas | Eje X: `dim_periodo[anio]` · Leyenda: `fact_demanda_sena[sector_economico]` · Valor: `[Total Inscritos]` | Comparativa por nivel |
| Segmentador | `fact_demanda_sena[sector_economico]` | (nivel de formación SENA) |

---

### Página 3: Brechas Laborales

| Visual | Datos | Configuración |
|--------|-------|---------------|
| Gráfico de área | Eje X: `dim_periodo[Periodo Etiqueta]` · Valor: `fact_mercado_laboral[tasa_desocupacion]` | Mostrar media como línea |
| Tarjeta | `[Brecha TD vs Promedio]` | Color condicional |
| Tarjeta | `[Alerta TD Alta]` | Icono semáforo |
| Tabla | `dim_periodo[anio]`, `dim_periodo[mes]`, `tasa_desocupacion`, `tasa_ocupacion`, `tasa_global_participacion`, `variacion_anual_td` | Formato condicional en TD |
| Gráfico de dispersión | Eje X: `tasa_global_participacion` · Eje Y: `tasa_desocupacion` · Tamaño: `tasa_ocupacion` | Por periodo |

---

### Página 4: Predicción IA

| Visual | Datos | Configuración |
|--------|-------|---------------|
| Gráfico de líneas combinado | **Histórico:** Eje X `dim_periodo[fecha_inicio]`, Valores `tasa_desocupacion` · **Forecast:** agregar marcadores en `prediccion_td[fecha]` vs `td_predicha` | Ver nota* |
| Área sombreada / barras de error | `prediccion_td[td_lower]` y `prediccion_td[td_upper]` | Representa IC 95% |
| Tarjeta | `[MAE Modelo]` | Etiqueta: "Error Absoluto Medio (pp)" |
| Tarjeta | `[RMSE Modelo]` | |
| Tarjeta | `[Nombre Modelo]` | |
| Tabla | `prediccion_td[fecha]`, `td_predicha`, `td_lower`, `td_upper` | Formato condicional |

**(*) Combinar histórico + forecast en un solo gráfico:**
1. Crear tabla calculada `Serie_Combinada`:
```dax
Serie_Combinada =
UNION(
    SELECTCOLUMNS(
        FILTER(fact_mercado_laboral, NOT ISBLANK(fact_mercado_laboral[tasa_desocupacion])),
        "Fecha", RELATED(dim_periodo[fecha_inicio]),
        "TD", fact_mercado_laboral[tasa_desocupacion],
        "Tipo", "Histórico",
        "Lower", BLANK(),
        "Upper", BLANK()
    ),
    SELECTCOLUMNS(
        prediccion_td,
        "Fecha", prediccion_td[fecha],
        "TD", prediccion_td[td_predicha],
        "Tipo", "Predicción",
        "Lower", prediccion_td[td_lower],
        "Upper", prediccion_td[td_upper]
    )
)
```
2. Gráfico de líneas: Eje X = `Fecha`, Valor = `TD`, Leyenda = `Tipo`

---

## 6. Formato global recomendado

- Tema: **Ejecutivo** (oscuro) o **Innovación** — menú Vista → Temas
- Colores clave:
  - Histórico: `#1F77B4` (azul)
  - Predicción: `#FF7F0E` (naranja)
  - Alerta alta: `#D62728` (rojo)
  - OK: `#2CA02C` (verde)
- Fuente títulos: Segoe UI Semibold 14pt
- Encabezado de página con logo MinTIC + texto "Mercado Laboral Colombia 2023-2026"
