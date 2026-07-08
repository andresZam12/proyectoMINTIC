# Conclusiones

## Resultados del modelo

El modelo Holt-Winters alcanzó un **MAE de 0,43 puntos porcentuales** y un **RMSE de 0,54 pp** sobre el conjunto de prueba (7 meses), superando en ambas métricas los criterios de éxito definidos (≤ 1,0 pp y ≤ 1,5 pp respectivamente). Que el RMSE sea solo ligeramente mayor que el MAE indica que los errores grandes son poco frecuentes: el modelo no tiene predicciones completamente erradas en ningún punto del período de evaluación.

## Tendencias identificadas

1. **Tendencia bajista sostenida:** la tasa de desocupación colombiana descendió de aproximadamente 11% en mayo de 2023 a cerca del 8,5% a finales de 2025, una caída de más de 2 puntos porcentuales en menos de tres años.

2. **Estacionalidad anual clara:** el desempleo sube en enero-febrero (inicio de año, menor actividad económica) y baja durante el segundo semestre, un patrón consistente en todos los años de la serie.

3. **Informalidad estructuralmente alta:** ciudades como Quibdó, Sincelejo y Cúcuta mantienen tasas de informalidad superiores al 65%, mientras que Bogotá, Medellín y Manizales están por debajo del 48%. Las diferencias entre ciudades son estadísticamente significativas (confirmado por el análisis ANOVA).

4. **Predicción H2 2026:** el modelo proyecta que la tasa de desocupación se mantendrá entre **6,5% y 9,0%** durante el segundo semestre de 2026, con tendencia estable o levemente decreciente.

## Aprendizajes técnicos

- Los boletines PDF del DANE, aunque son documentos públicos, no tienen estructura de datos estandarizada entre ediciones. La estrategia de dos fases (regex + extracción de tablas) fue necesaria para lograr cobertura del 100% de los 34 boletines.
- Los archivos Excel de informalidad del MinTrabajo presentan un problema sutil con los trimestres móviles que cruzan años: "Nov21-Ene22" asigna el enero al año incorrecto si no se maneja con offset. Este tipo de error es silencioso y produce fechas incorrectas sin fallar explícitamente.
- Prophet, a pesar de ser la herramienta más moderna, requiere un compilador C++ (CmdStan/Stan) que no está disponible por defecto en Windows. Holt-Winters demostró ser una alternativa completamente válida para esta serie.

## Limitaciones

- La serie temporal tiene solo 34 puntos, insuficientes para capturar ciclos económicos largos (recesiones, recuperaciones post-crisis).
- El modelo no incorpora variables exógenas con correlación conocida con el desempleo (PIB, precio del petróleo, tasa de cambio).
- Los datos del SENA solo cubren 2019-2020, lo que impide comparar la demanda de formación con el período post-pandemia.
- Las zonas rurales y municipios pequeños no están representados en los datos de informalidad, que cubren solo 23 ciudades principales.

## Valor público generado

Esta solución transforma datos abiertos que estaban dispersos en PDFs, Excel y APIs separadas en un sistema integrado y accesible que:

- Reduce de horas a segundos el tiempo para consultar la evolución del mercado laboral colombiano
- Permite anticipar períodos críticos de desempleo con 6 meses de antelación
- Está disponible públicamente sin costo ni software adicional en `economia-empleo.vercel.app`
- Es reproducible y extensible por cualquier equipo o entidad que lo necesite

## Trabajo futuro

- Incorporar series históricas del DANE desde 2010 para mejorar la captura de ciclos económicos
- Añadir variables exógenas (PIB trimestral, índice de confianza empresarial) para un modelo multivariado
- Automatizar la actualización mensual con un job programado en la infraestructura de Vercel
- Extender el análisis de informalidad a nivel municipal usando microdatos GEIH
