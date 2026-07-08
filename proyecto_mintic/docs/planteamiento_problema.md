# Planteamiento del Problema

## Contexto

Colombia tiene históricamente una de las tasas de desempleo más altas de América Latina, con un promedio cercano al 11% en 2023 y variaciones estacionales marcadas: el desempleo sube en enero-febrero (inicio de año, menor actividad económica) y baja durante el segundo semestre. A esto se suman diferencias regionales importantes: ciudades como Quibdó o Cúcuta presentan tasas de informalidad superiores al 70%, mientras que Bogotá o Medellín están por debajo del 50%.

Sin embargo, toda esa información está fragmentada en fuentes distintas con formatos distintos:

- Los **boletines del DANE** son PDFs mensuales de entre 15 y 30 páginas, sin estructura de datos estandarizada.
- Las **estadísticas de informalidad laboral** las publica el MinTrabajo en archivos Excel trimestrales con encabezados en dos filas y trimestres móviles que cruzan años calendario.
- Los **datos de demanda de formación del SENA** están disponibles como API JSON en datos.gov.co pero no están cruzados con los indicadores de desempleo.
- Los **microdatos GEIH** contienen millones de registros crudos que requieren procesamiento especializado antes de poder usarse.

## Problema específico

No existe un punto de consulta integrado donde un tomador de decisiones pueda ver, en un solo lugar:

1. Cómo ha evolucionado la tasa de desempleo en los últimos años
2. Qué tan informal es el trabajo en cada ciudad colombiana
3. Qué ocupaciones tiene mayor demanda de formación según el SENA
4. Hacia dónde apunta la tendencia del desempleo en los próximos 6 meses

Todo eso existe en datos abiertos, pero nadie lo había cruzado en una sola solución funcional y accesible.

## Pregunta de investigación

> ¿Es posible construir un sistema predictivo que integre múltiples fuentes de datos abiertos del mercado laboral colombiano y proyecte la tasa de desocupación a 6 meses con un error promedio inferior a 1 punto porcentual?

## Alcance

- **Temporal:** serie histórica mayo 2023 – febrero 2026; predicciones hasta agosto 2026
- **Geográfico:** nivel nacional para predicción; 23 ciudades principales para análisis de informalidad
- **Poblacional:** fuerza laboral colombiana (personas en edad de trabajar, 15 años o más)
- **Fuera de alcance:** microdatos individuales del GEIH, análisis por género para la predicción principal, datos en tiempo real
