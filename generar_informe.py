"""
generar_informe.py
Genera el PDF de resumen del proyecto MinTIC 2026.
Ejecutar desde la raíz: python generar_informe.py
"""

import os
import sys
from fpdf import FPDF
from fpdf.enums import XPos, YPos

RUTA_PDF = os.path.join(os.path.dirname(__file__), "Informe_ProyectoMinTIC_2026.pdf")

# ── Paleta de colores ─────────────────────────────────────────────
AZUL_OSCURO  = (26,  54,  93)
AZUL_MEDIO   = (41,  98, 158)
AZUL_CLARO   = (189, 215, 238)
VERDE        = (56, 142,  60)
NARANJA      = (230, 126,  34)
GRIS_TEXTO   = (50,  50,  50)
GRIS_FONDO   = (245, 245, 245)
BLANCO       = (255, 255, 255)
ROJO_MINTIC  = (139,  0,   0)


class PDF(FPDF):

    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*AZUL_OSCURO)
        self.rect(0, 0, 210, 12, "F")
        self.set_text_color(*BLANCO)
        self.set_font("Helvetica", "B", 8)
        self.set_xy(10, 3)
        self.cell(0, 6, "Dashboard Predictivo del Mercado Laboral Colombiano  |  MinTIC 2026",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*GRIS_TEXTO)
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_fill_color(*AZUL_OSCURO)
        self.rect(0, self.get_y(), 210, 15, "F")
        self.set_text_color(*BLANCO)
        self.set_font("Helvetica", "", 8)
        self.cell(0, 8, f"Pagina {self.page_no()}  |  Equipo: Andres, Daniers, Deivid  |  Fecha limite: 30 de abril 2026",
                  align="C")

    # ── Helpers de estilo ──────────────────────────────────────────
    def titulo_seccion(self, texto):
        self.set_fill_color(*AZUL_OSCURO)
        self.set_text_color(*BLANCO)
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 9, f"  {texto}", fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        self.set_text_color(*GRIS_TEXTO)

    def subtitulo(self, texto):
        self.set_text_color(*AZUL_MEDIO)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 7, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*GRIS_TEXTO)

    def parrafo(self, texto, size=9):
        self.set_font("Helvetica", "", size)
        self.set_text_color(*GRIS_TEXTO)
        self.multi_cell(0, 5, texto)
        self.ln(1)

    def bullet(self, texto, color=AZUL_MEDIO):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*color)
        self.cell(6, 5, "-")
        self.set_text_color(*GRIS_TEXTO)
        self.multi_cell(0, 5, texto)

    def badge(self, texto, color_fondo, color_texto=None):
        if color_texto is None:
            color_texto = BLANCO
        self.set_fill_color(*color_fondo)
        self.set_text_color(*color_texto)
        self.set_font("Helvetica", "B", 8)
        self.cell(len(texto) * 2.5 + 6, 6, f" {texto} ", fill=True)
        self.set_text_color(*GRIS_TEXTO)

    def fila_tabla(self, cols, anchos, fondo=None, negrita=False):
        if fondo:
            self.set_fill_color(*fondo)
        font_style = "B" if negrita else ""
        self.set_font("Helvetica", font_style, 8.5)
        for texto, ancho in zip(cols, anchos):
            self.cell(ancho, 7, str(texto),
                      border=1, fill=bool(fondo),
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.ln()

    def linea_separadora(self):
        self.set_draw_color(*AZUL_CLARO)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)


# ── Portada ───────────────────────────────────────────────────────
def portada(pdf: PDF):
    # Fondo superior
    pdf.set_fill_color(*AZUL_OSCURO)
    pdf.rect(0, 0, 210, 80, "F")

    # Franja de acento
    pdf.set_fill_color(*ROJO_MINTIC)
    pdf.rect(0, 78, 210, 6, "F")

    pdf.set_xy(10, 15)
    pdf.set_text_color(*BLANCO)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "CONCURSO DATOS AL ECOSISTEMA 2026  |  MinTIC",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_xy(10, 22)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 5, "Materia: Herramientas Computacionales para la Interpretacion de Resultados",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_xy(10, 35)
    pdf.set_font("Helvetica", "B", 22)
    pdf.multi_cell(190, 12, "Dashboard Predictivo del\nMercado Laboral Colombiano")

    pdf.set_xy(10, 65)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Pipeline: DataSource -> DataProcess -> DataTransform -> DataProduct")

    # Tarjetas de equipo
    y_cards = 92
    equipos = [
        ("Andres", "Arquitectura, PySpark, Modelo IA", AZUL_MEDIO),
        ("Daniers", "Validacion datos, Power BI pags 1 y 3", (56, 142, 60)),
        ("Deivid", "Scripts extraccion, Power BI pags 2 y 4", (139, 0, 0)),
    ]
    for i, (nombre, rol, color) in enumerate(equipos):
        x = 10 + i * 65
        pdf.set_fill_color(*color)
        pdf.rect(x, y_cards, 62, 20, "F")
        pdf.set_text_color(*BLANCO)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_xy(x + 2, y_cards + 2)
        pdf.cell(58, 6, nombre)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_xy(x + 2, y_cards + 10)
        pdf.multi_cell(58, 4, rol)

    pdf.set_text_color(*GRIS_TEXTO)
    pdf.set_xy(10, 122)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "Stack: Python  |  Scrapy  |  Selenium  |  PySpark  |  PostgreSQL  |  Docker  |  Power BI  |  Prophet")

    # Fecha límite
    pdf.set_fill_color(*ROJO_MINTIC)
    pdf.rect(10, 132, 190, 14, "F")
    pdf.set_text_color(*BLANCO)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_xy(10, 135)
    pdf.cell(190, 8, "FECHA LIMITE DE ENTREGA: 30 DE ABRIL DE 2026", align="C")

    pdf.set_text_color(*GRIS_TEXTO)
    pdf.set_xy(10, 155)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 5, f"Informe generado el 22 de abril de 2026")


# ── Pagina 2: Contexto y Objetivos ───────────────────────────────
def pagina_contexto(pdf: PDF):
    pdf.add_page()

    pdf.titulo_seccion("1. CONTEXTO DEL PROYECTO")
    pdf.parrafo(
        "Este proyecto tiene doble proposito: participar en el concurso nacional "
        "Datos al Ecosistema 2026 organizado por el MinTIC, y ser entregado como "
        "trabajo final de la materia Herramientas Computacionales para la "
        "Interpretacion de Resultados (6. semestre de Ingenieria de Software). "
        "Ambos escenarios se cumplen con el mismo entregable."
    )

    pdf.set_fill_color(*AZUL_CLARO)
    pdf.rect(10, pdf.get_y(), 190, 18, "F")
    pdf.set_text_color(*AZUL_OSCURO)
    pdf.set_font("Helvetica", "BI", 9)
    pdf.set_x(15)
    pdf.multi_cell(180, 5,
        "\"Construir tableros inteligentes que identifiquen tendencias de empleo y "
        "sectores emergentes usando datos abiertos de datos.gov.co.\"\n"
        "-- Reto oficial MinTIC, Categoria: Economia y Empleo"
    )
    pdf.ln(5)
    pdf.set_text_color(*GRIS_TEXTO)

    pdf.titulo_seccion("2. OBJETIVOS DEL PROYECTO")

    headers = ["#", "Objetivo", "Descripcion", "Tipo"]
    anchos  = [10,  35, 115, 30]
    pdf.fila_tabla(headers, anchos, fondo=AZUL_OSCURO, negrita=True)
    pdf.set_text_color(*BLANCO)

    filas = [
        ("O1", "Panorama Nacional",  "Describir el estado actual del mercado laboral por departamento", "Descriptivo"),
        ("O2", "Sectores Emergentes","Identificar sectores con mayor crecimiento y caida de empleo",   "Comparativo"),
        ("O3", "Brechas Laborales",  "Analizar brechas por genero, edad, educacion y zona",            "Diagnostico"),
        ("O4", "Prediccion IA",      "Predecir tasa de desocupacion para los proximos 6 meses",        "Predictivo"),
    ]
    fondos = [GRIS_FONDO, BLANCO, GRIS_FONDO, (220, 255, 220)]
    for fila, fondo in zip(filas, fondos):
        pdf.fila_tabla(fila, anchos, fondo=fondo)

    pdf.ln(5)
    pdf.titulo_seccion("3. CRITERIOS DE EVALUACION (100 pts)")

    criterios = [
        ("Uso de datos abiertos", "20", "4 fuentes oficiales colombianas + API Socrata"),
        ("Uso de IA",             "20", "Modelo predictivo + metricas MAE/RMSE"),
        ("Impacto y escalabilidad","20","Cobertura nacional, replicable con Docker"),
        ("Analisis y rigor tecnico","15","CRISP-ML, PySpark, PostgreSQL, 20 variables"),
        ("Innovacion y creatividad","15","Pipeline DataSource->DataProduct integrado con IA"),
        ("Diseno y usabilidad",    "10","Dashboard 4 paginas con filtros globales"),
    ]
    pdf.fila_tabla(["Criterio", "Pts", "Como lo cubre el proyecto"],
                   [70, 15, 105], fondo=AZUL_OSCURO, negrita=True)
    for i, (c, p, d) in enumerate(criterios):
        fondo = GRIS_FONDO if i % 2 == 0 else BLANCO
        pdf.fila_tabla([c, p, d], [70, 15, 105], fondo=fondo)


# ── Pagina 3: Arquitectura ────────────────────────────────────────
def pagina_arquitectura(pdf: PDF):
    pdf.add_page()

    pdf.titulo_seccion("4. ARQUITECTURA DEL PIPELINE")
    pdf.parrafo(
        "El proyecto implementa un pipeline de datos de 4 etapas, desde la extraccion "
        "de fuentes abiertas hasta el dashboard final en Power BI. Todo corre localmente "
        "en Windows 11 con Docker Desktop - sin servidor externo ni cuenta de nube."
    )

    # Diagrama de pipeline
    etapas = [
        ("F1  DataSource",   "requests + Selenium\n+ Scrapy",
         "Portales DANE,\nFILCO, SENA",         "CSV / Excel / PDF\nen data/raw/"),
        ("F2  DataProcess",  "pandas + pdfplumber",
         "data/raw/",                             "Data Lake validado\n+ metadata.json"),
        ("F3  DataTransform","PySpark + PostgreSQL\n+ JDBC",
         "Data Lake validado",                    "5 tablas limpias\nen PostgreSQL 15"),
        ("F4  DataProduct",  "Power BI + Prophet",
         "PostgreSQL\nlocalhost:5432",            "Dashboard 4 paginas\n+ forecast 6 meses"),
    ]
    colores_etapa = [AZUL_MEDIO, (56,142,60), (230,126,34), ROJO_MINTIC]

    y0 = pdf.get_y()
    for i, (etapa, herramienta, entrada, salida) in enumerate(etapas):
        x = 10 + i * 48
        color = colores_etapa[i]

        # Cabecera de etapa
        pdf.set_fill_color(*color)
        pdf.rect(x, y0, 45, 8, "F")
        pdf.set_text_color(*BLANCO)
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_xy(x + 1, y0 + 1)
        pdf.multi_cell(43, 3.5, etapa)

        # Cuerpo
        pdf.set_fill_color(*GRIS_FONDO)
        pdf.rect(x, y0 + 8, 45, 34, "F")
        pdf.set_draw_color(*color)
        pdf.rect(x, y0, 45, 42)
        pdf.set_text_color(*AZUL_OSCURO)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_xy(x + 2, y0 + 9)
        pdf.cell(41, 4, "Herramienta:")
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*GRIS_TEXTO)
        pdf.set_xy(x + 2, y0 + 13)
        pdf.multi_cell(41, 3.5, herramienta)
        pdf.set_text_color(*AZUL_OSCURO)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_xy(x + 2, y0 + 25)
        pdf.cell(41, 4, "Salida:")
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*GRIS_TEXTO)
        pdf.set_xy(x + 2, y0 + 29)
        pdf.multi_cell(41, 3.5, salida)

        # Flecha
        if i < 3:
            pdf.set_draw_color(*AZUL_OSCURO)
            pdf.set_line_width(0.8)
            fx = x + 45
            fy = y0 + 21
            pdf.line(fx, fy, fx + 2.5, fy)
            pdf.set_fill_color(*AZUL_OSCURO)
            pdf.polygon([(fx+2.5, fy-1.5),(fx+2.5, fy+1.5),(fx+4.5, fy)], style="F")
            pdf.set_line_width(0.2)

    pdf.ln(48)

    pdf.titulo_seccion("5. STACK TECNOLOGICO")
    capas = [
        ("Entorno",        "Docker Desktop",              "Orquesta PostgreSQL + Jupyter sin conflictos"),
        ("Extraccion",     "Python 3.13, requests 2.31",  "Lenguaje base + descarga de APIs REST (SENA, DANE)"),
        ("Extraccion",     "Scrapy 2.11, Selenium 4.18",  "Portales con paginacion JS (GEIH, FILCO)"),
        ("Procesamiento",  "pandas 2.2, openpyxl 3.1",    "Validacion, exploracion del Data Lake, lectura Excel"),
        ("Procesamiento",  "pdfplumber 0.11",              "Extraccion de tablas e indicadores de PDFs DANE"),
        ("Transformacion", "PySpark 3.x",                 "Limpieza masiva GEIH via Docker"),
        ("Base de datos",  "PostgreSQL 15",               "Almacen final de 5 tablas limpias"),
        ("Modelo IA",      "Prophet 1.3 / statsmodels",   "Series de tiempo -> prediccion TD 6 meses"),
        ("Modelo IA",      "scikit-learn 1.4",            "Metricas MAE / RMSE del modelo"),
        ("Visualizacion",  "Power BI Desktop",            "Dashboard final 4 paginas"),
    ]
    colores_capa = {
        "Entorno": (200, 220, 240),
        "Extraccion": (220, 240, 220),
        "Procesamiento": (255, 243, 205),
        "Transformacion": (235, 220, 255),
        "Base de datos": (200, 220, 240),
        "Modelo IA": (220, 255, 220),
        "Visualizacion": (255, 220, 220),
    }
    pdf.fila_tabla(["Capa", "Herramienta", "Para que se usa"],
                   [38, 52, 100], fondo=AZUL_OSCURO, negrita=True)
    for capa, herr, uso in capas:
        fondo = colores_capa.get(capa, GRIS_FONDO)
        pdf.fila_tabla([capa, herr, uso], [38, 52, 100], fondo=fondo)


# ── Pagina 4: Fuentes de Datos ────────────────────────────────────
def pagina_fuentes(pdf: PDF):
    pdf.add_page()

    pdf.titulo_seccion("6. FUENTES DE DATOS")
    fuentes = [
        ("SENA APE",       "SENA",        "datos.gov.co/resource/8pqf-rmzr",  "Listo",    "566 registros, API Socrata, datos 2019-2020"),
        ("Boletines DANE", "DANE",         "dane.gov.co/files/operaciones/GEIH","Listo",   "34 PDFs may2023-feb2026, ~20 MB"),
        ("GEIH 2024",      "DANE",         "microdatos.dane.gov.co/catalog/819","Pendiente","Microdatos individuales GEIH"),
        ("GEIH 2025",      "DANE",         "microdatos.dane.gov.co/catalog/853","Pendiente","Microdatos individuales GEIH"),
        ("FILCO",          "MinTrabajo",   "filco.mintrabajo.gov.co",           "Pendiente","Formalidad e informalidad laboral"),
    ]
    pdf.fila_tabla(["Fuente","Entidad","URL (resumen)","Estado","Detalle"],
                   [28,22,60,22,58], fondo=AZUL_OSCURO, negrita=True)
    for f in fuentes:
        fondo = (220,255,220) if f[3]=="Listo" else (255,243,205)
        pdf.fila_tabla(f, [28,22,60,22,58], fondo=fondo)

    pdf.ln(4)
    pdf.titulo_seccion("7. TABLAS EN POSTGRESQL (mintic_db)")
    tablas = [
        ("dim_departamento", "Catalogo de 23 departamentos + codigos DANE", "GEIH / Boletines",   "DDL listo"),
        ("dim_periodo",      "Calendario mes-anio 2010-2026",               "Generada PySpark",   "DDL listo"),
        ("fact_mercado_laboral","TD, TO, TGP, ingresos, sector, sexo, edad, zona","GEIH+FILCO+DANE","DDL listo"),
        ("fact_demanda_sena","Inscritos y vacantes por ocupacion",          "SENA datos.gov.co",  "DDL listo"),
        ("prediccion_td",   "Forecast 6 meses generado por modelo IA",     "Modelo Python",      "Poblado"),
    ]
    pdf.fila_tabla(["Tabla","Contenido","Fuente","Estado"],
                   [40,75,50,25], fondo=AZUL_OSCURO, negrita=True)
    for i, t in enumerate(tablas):
        fondo = GRIS_FONDO if i%2==0 else BLANCO
        if t[3] == "Poblado":
            fondo = (220,255,220)
        pdf.fila_tabla(t, [40,75,50,25], fondo=fondo)

    pdf.ln(4)
    pdf.titulo_seccion("8. VARIABLES DEL PROYECTO (20 funcionales)")
    variables = [
        ("tasa_desocupacion",         "% personas buscando empleo / PEA",            "GEIH",     "O1, O4"),
        ("tasa_ocupacion",            "% personas ocupadas / PET",                   "GEIH",     "O1, O4"),
        ("tasa_global_participacion", "PEA / PET",                                   "GEIH",     "O1"),
        ("rama_actividad",            "Sector economico del ocupado (CIIU)",         "GEIH",     "O2"),
        ("posicion_ocupacional",      "Empleado, independiente, patron, domestico",  "GEIH",     "O2, O3"),
        ("ingreso_laboral",           "Ingreso mensual promedio en pesos",           "GEIH",     "O2, O3"),
        ("nivel_educativo",           "Ninguno/primaria/secundaria/tecnico/prof.",   "GEIH",     "O3"),
        ("sexo",                      "Hombre / Mujer",                              "GEIH",     "O3"),
        ("grupo_edad",                "Rangos: 15-28, 29-45, 46-65+",               "GEIH",     "O3"),
        ("zona",                      "Cabecera urbana / Rural disperso",            "GEIH",     "O3"),
        ("departamento",              "23 departamentos + areas metropolitanas",     "GEIH",     "O1, O3"),
        ("periodo",                   "Mes y anio de la medicion",                   "GEIH",     "O1, O4"),
        ("tasa_formalidad",           "% ocupados con contrato + seguridad social",  "FILCO",    "O2, O3"),
        ("tasa_informalidad",         "% ocupados sin proteccion laboral formal",    "FILCO",    "O2, O3"),
        ("afiliacion_seg_social",     "Cobertura salud y pension por region",        "FILCO",    "O3"),
        ("inscritos_por_depto",       "Personas buscando empleo activamente via SENA","SENA",    "O1, O2"),
        ("vacantes_por_oficio",       "Cargos mas demandados por empleadores",       "SENA",     "O2"),
        ("variacion_anual_TD",        "TD anio actual - TD anio anterior (SQL)",     "Calculada","O1"),
        ("brecha_genero_empleo",      "TD mujeres - TD hombres por periodo (SQL)",   "Calculada","O3"),
        ("prediccion_TD_6meses",      "Modelo IA entrenado con serie 2023-2026",     "IA Python","O4"),
    ]
    pdf.fila_tabla(["Variable","Descripcion","Fuente","Obj."],
                   [52,90,22,26], fondo=AZUL_OSCURO, negrita=True)
    colores_fuente = {"GEIH":(220,240,255),"FILCO":(255,243,205),
                      "SENA":(220,255,220),"Calculada":(235,220,255),"IA Python":(220,255,220)}
    for v in variables:
        fondo = colores_fuente.get(v[2], GRIS_FONDO)
        pdf.fila_tabla(v, [52,90,22,26], fondo=fondo)


# ── Pagina 5: Lo que hemos hecho ──────────────────────────────────
def pagina_hecho(pdf: PDF):
    pdf.add_page()

    pdf.titulo_seccion("9. LO QUE HEMOS IMPLEMENTADO")

    secciones = [
        ("F1 - DataSource: Extraccion de datos", VERDE, [
            "extraccion_sena.py - API Socrata datos.gov.co: 566 registros descargados y guardados en data/raw/sena/sena_inscritos.csv",
            "extraccion_dane_boletines.py - 34 boletines PDF GEIH del DANE (may2023 a feb2026), ~20 MB en data/raw/dane_boletines/",
            "extraccion_geih.py - Script Selenium headless para catalogo DANE (/catalog/819 y /catalog/853), acepta terminos automaticamente",
            "extraccion_filco.py - Intento directo via requests + fallback Selenium para datos de formalidad/informalidad",
        ]),
        ("F2 - DataProcess: Validacion y parseo", AZUL_MEDIO, [
            "validar_datos.py - Valida 4 fuentes de datos, calcula MD5, cuenta nulos/duplicados, genera data/raw/metadata.json",
            "parsear_boletines.py - Extrae TD, TO y TGP de los 34 PDFs usando pdfplumber con 3 patrones regex adaptativos",
            "34 de 34 PDFs parseados correctamente. Serie temporal: may2023 - feb2026",
            "Maneja dos formatos historicos: 'tasa de desempleo' (may-jun2023) y 'tasa de desocupacion' (ago2023 en adelante)",
        ]),
        ("F3 - DataTransform: PySpark + PostgreSQL", NARANJA, [
            "crear_tablas.sql - DDL completo de 5 tablas con indices, constraints y catalogo dim_departamento pre-poblado (30 filas)",
            "transformar.py - PySpark: limpieza SENA, carga serie temporal boletines y microdatos GEIH a PostgreSQL via JDBC",
            "Mapeo de columnas Socrata -> modelo relacional, decodificacion de codigos DANE (sexo, zona, grupo_edad)",
            "docker-compose.yml levanta PostgreSQL 15 y Jupyter con un solo comando: docker-compose up -d",
        ]),
        ("F3B - Modelo IA: Prediccion TD", VERDE, [
            "modelo_prophet.py - Entrena modelo de series de tiempo con la serie TD may2023-feb2026",
            "Backend dual: intenta Prophet primero; usa Holt-Winters (statsmodels) como fallback si CmdStan no compila",
            "Validacion con 20% de datos (ultimos 6 meses como conjunto de prueba)",
            "Resultados: MAE = 0.43 pp  |  RMSE = 0.54 pp  (excelente para la volatilidad de la TD colombiana)",
            "Predicciones guardadas en data/processed/prediccion_td.csv y grafica en data/processed/forecast_prophet.png",
        ]),
    ]

    for titulo, color, items in secciones:
        pdf.set_fill_color(*color)
        pdf.rect(10, pdf.get_y(), 4, len(items)*5+12, "F")
        pdf.set_text_color(*color)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_x(17)
        pdf.cell(0, 7, titulo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(*GRIS_TEXTO)
        for item in items:
            pdf.set_x(17)
            pdf.set_font("Helvetica", "", 8.5)
            pdf.cell(5, 5, "-")
            pdf.multi_cell(175, 5, item)
        pdf.ln(3)


# ── Pagina 6: Resultados del modelo IA ───────────────────────────
def pagina_modelo(pdf: PDF):
    pdf.add_page()

    pdf.titulo_seccion("10. RESULTADOS DEL MODELO IA")

    # Metricas
    pdf.subtitulo("Metricas de evaluacion (conjunto de prueba: sep2025 - feb2026)")
    pdf.ln(2)
    metricas = [("MAE (Error Absoluto Medio)", "0.4344 pp", "Excelente - el modelo se equivoca 0.43 puntos en promedio"),
                ("RMSE (Raiz del ECM)",         "0.5368 pp", "Muy bueno - penaliza errores grandes, sigue siendo bajo"),
                ("Periodo de entrenamiento",    "may2023 - ago2025", "28 meses de datos reales DANE"),
                ("Periodo de prueba",           "sep2025 - feb2026", "6 meses de validacion out-of-sample"),
                ("Backend utilizado",           "Holt-Winters (statsmodels)", "Prophet como primera opcion; fallback sin compilador C++"),]
    pdf.fila_tabla(["Metrica","Valor","Interpretacion"],
                   [60,50,80], fondo=AZUL_OSCURO, negrita=True)
    for i, m in enumerate(metricas):
        pdf.fila_tabla(m, [60,50,80], fondo=GRIS_FONDO if i%2==0 else BLANCO)

    pdf.ln(5)
    pdf.subtitulo("Predicciones para los proximos 4 meses (desde hoy: 22 abr 2026)")
    pdf.ln(2)
    predicciones = [
        ("Mayo 2026",   "8.04%", "7.17%", "8.92%", "Estable"),
        ("Junio 2026",  "7.51%", "6.64%", "8.38%", "Leve baja estacional"),
        ("Julio 2026",  "7.54%", "6.67%", "8.42%", "Recuperacion"),
        ("Agosto 2026", "7.31%", "6.44%", "8.18%", "Continuacion baja"),
    ]
    pdf.fila_tabla(["Mes","TD Predicha","Intervalo Inf. 80%","Intervalo Sup. 80%","Tendencia"],
                   [36,28,38,38,50], fondo=AZUL_OSCURO, negrita=True)
    for i, p in enumerate(predicciones):
        pdf.fila_tabla(p, [36,28,38,38,50], fondo=(220,255,220) if i%2==0 else BLANCO)

    pdf.ln(5)
    pdf.subtitulo("Serie historica TD Colombia (extraida de boletines DANE)")
    pdf.ln(2)
    datos_hist = [
        ("2023", "May-Dic", "9.3% - 10.5%", "Tendencia descendente gradual"),
        ("2024", "Ene-Jun", "10.3% - 12.7%", "Pico enero (estacionalidad), luego descenso"),
        ("2024", "Jul-Dic", "8.2% - 9.9%",   "Mejora sostenida segundo semestre"),
        ("2025", "Ene-Jun", "8.8% - 11.6%",  "Pico enero, descenso rapido"),
        ("2025", "Jul-Dic", "7.0% - 8.8%",   "Minimos historicos recientes"),
        ("2026", "Ene-Feb", "9.2% - 10.9%",  "Repunte estacional de inicio de anio"),
    ]
    pdf.fila_tabla(["Anio","Meses","Rango TD","Observacion"],
                   [20,24,40,106], fondo=AZUL_OSCURO, negrita=True)
    for i, d in enumerate(datos_hist):
        pdf.fila_tabla(d, [20,24,40,106], fondo=GRIS_FONDO if i%2==0 else BLANCO)

    pdf.ln(5)
    pdf.set_fill_color(*AZUL_CLARO)
    pdf.rect(10, pdf.get_y(), 190, 22, "F")
    pdf.set_text_color(*AZUL_OSCURO)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_x(15)
    pdf.cell(0, 7, "Interpretacion de los resultados:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_x(15)
    pdf.multi_cell(180, 5,
        "La tasa de desocupacion colombiana muestra una tendencia descendente sostenida: de ~10.5% (may2023) "
        "a ~7-8% (fin2025). El modelo predice que esta tendencia continua con TD entre 7.3% y 8.0% "
        "para el segundo semestre 2026. El MAE de 0.43 pp es competitivo con modelos ARIMA publicados para "
        "series laborales latinoamericanas."
    )
    pdf.set_text_color(*GRIS_TEXTO)


# ── Pagina 7: Estado y pendientes ────────────────────────────────
def pagina_estado(pdf: PDF):
    pdf.add_page()

    pdf.titulo_seccion("11. ESTADO ACTUAL DEL PIPELINE (22 ABR 2026)")

    scripts = [
        ("extraccion_sena.py",          "F1","Ejecutado","566 registros CSV · API Socrata OK",                 VERDE),
        ("extraccion_dane_boletines.py","F1","Ejecutado","34 PDFs descargados · 20.3 MB",                     VERDE),
        ("extraccion_geih.py",          "F1","Escrito",  "Script Selenium listo · requiere portal DANE",       NARANJA),
        ("extraccion_filco.py",         "F1","Escrito",  "Script Selenium + requests listo",                   NARANJA),
        ("validar_datos.py",            "F2","Ejecutado","metadata.json generado · 2 fuentes OK, 2 pendientes",VERDE),
        ("parsear_boletines.py",        "F2","Ejecutado","34/34 PDFs · serie_temporal_td.csv lista",           VERDE),
        ("crear_tablas.sql",            "F3","Listo",    "Se ejecuta automaticamente con Docker",              (41,98,158)),
        ("transformar.py",              "F3","Escrito",  "Requiere Docker corriendo",                          NARANJA),
        ("modelo_prophet.py",           "F3B","Ejecutado","MAE=0.43 pp · prediccion_td.csv + PNG",            VERDE),
        ("Power BI Dashboard",          "F4","Pendiente","4 paginas a construir manualmente",                  ROJO_MINTIC),
        ("CRISP-ML + GitHub",           "F5","Pendiente","Documentacion metodologica + repo publico",          ROJO_MINTIC),
    ]

    pdf.fila_tabla(["Script / Entregable","Fase","Estado","Detalle"],
                   [60,12,22,96], fondo=AZUL_OSCURO, negrita=True)
    for s in scripts:
        nombre, fase, estado, detalle, color = s
        fondo_estado = {
            "Ejecutado": (220,255,220),
            "Escrito":   (255,243,205),
            "Listo":     (220,240,255),
            "Pendiente": (255,220,220),
        }.get(estado, GRIS_FONDO)
        pdf.set_fill_color(*fondo_estado)
        pdf.set_font("Helvetica", "", 8.5)
        x0 = pdf.get_x()
        y0 = pdf.get_y()
        pdf.cell(60, 7, nombre, border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(12, 7, fase,   border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_fill_color(*color)
        pdf.set_text_color(*BLANCO)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(22, 7, estado, border=1, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_fill_color(*fondo_estado)
        pdf.set_text_color(*GRIS_TEXTO)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.cell(96, 7, detalle, border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(5)
    pdf.titulo_seccion("12. PASOS INMEDIATOS (23-30 ABR 2026)")

    pasos = [
        ("23 abr", "Iniciar Docker Desktop y ejecutar docker-compose up -d"),
        ("23 abr", "Ejecutar transformar.py en el contenedor Jupyter para cargar datos a PostgreSQL"),
        ("23-24 abr", "Ejecutar extraccion_geih.py - descargar microdatos 2024/2025 del portal DANE"),
        ("24-25 abr", "Ejecutar extraccion_filco.py - datos formalidad/informalidad MinTrabajo"),
        ("26-29 abr", "Construir Power BI: conectar a localhost:5432 y disenar las 4 paginas"),
        ("29-30 abr", "Redactar documentacion CRISP-ML, subir a GitHub publico, registrar en datos.gov.co/usos"),
    ]
    for fecha, tarea in pasos:
        pdf.set_fill_color(*AZUL_OSCURO)
        pdf.set_text_color(*BLANCO)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(26, 7, f"  {fecha}", fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_fill_color(*GRIS_FONDO)
        pdf.set_text_color(*GRIS_TEXTO)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(164, 7, f"  {tarea}", fill=True, border="B",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(5)
    pdf.titulo_seccion("13. CREDENCIALES DOCKER (solo uso local)")
    creds = [
        ("PostgreSQL", "localhost:5432", "mintic_db", "mintic_user", "mintic2026"),
        ("Jupyter",    "localhost:8888", "--",        "token",       "mintic2026"),
    ]
    pdf.fila_tabla(["Servicio","Host:Puerto","Base de datos","Usuario","Password"],
                   [28,34,36,30,62], fondo=AZUL_OSCURO, negrita=True)
    for c in creds:
        pdf.fila_tabla(c, [28,34,36,30,62], fondo=GRIS_FONDO)


# ── Pagina 8: Dashboard Power BI ─────────────────────────────────
def pagina_powerbi(pdf: PDF):
    pdf.add_page()

    pdf.titulo_seccion("14. PLAN DEL DASHBOARD POWER BI (4 PAGINAS)")
    pdf.parrafo(
        "Power BI Desktop conectado a PostgreSQL localhost:5432. "
        "Filtros globales en todas las paginas: Departamento | Anio | Trimestre | Sexo | Sector economico."
    )

    paginas = [
        ("Pagina 1: Panorama Nacional", AZUL_MEDIO, "Daniers", "O1", [
            "KPIs destacados: TD, TO, TGP actuales vs anio anterior",
            "Mapa coroplético de departamentos coloreado por TD",
            "Linea de tiempo historica TD 2023-2026",
            "Tabla comparativa por departamento",
        ]),
        ("Pagina 2: Sectores y Empleo", (56,142,60), "Deivid", "O2", [
            "Barras horizontales por rama de actividad economica (CIIU)",
            "Treemap de sectores con mayor variacion de empleo",
            "Top 10 ocupaciones mas demandadas (SENA)",
            "Comparacion inscritos vs vacantes por oficio",
        ]),
        ("Pagina 3: Brechas Laborales", (230,126,34), "Daniers", "O3", [
            "Grafico comparativo TD Hombre vs Mujer por periodo",
            "Piramide de edad con tasa de ocupacion por grupo",
            "Mapa de formalidad vs informalidad por departamento (FILCO)",
            "Scatter: nivel educativo vs ingreso laboral promedio",
        ]),
        ("Pagina 4: Prediccion IA", ROJO_MINTIC, "Andres", "O4", [
            "Linea TD historica (may2023-feb2026) + forecast 6 meses",
            "Banda de intervalo de confianza 80% del modelo",
            "Tarjetas: MAE, RMSE, fecha de generacion del modelo",
            "Tabla de predicciones mensuales con valores exactos",
        ]),
    ]

    for titulo, color, resp, obj, vizs in paginas:
        pdf.set_fill_color(*color)
        pdf.rect(10, pdf.get_y(), 190, 8, "F")
        pdf.set_text_color(*BLANCO)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_x(12)
        pdf.cell(130, 8, titulo)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(30, 8, f"Resp: {resp}")
        pdf.cell(28, 8, f"Obj: {obj}")
        pdf.ln()
        pdf.set_text_color(*GRIS_TEXTO)
        for viz in vizs:
            pdf.set_x(15)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*color)
            pdf.cell(5, 5, "-")
            pdf.set_text_color(*GRIS_TEXTO)
            pdf.cell(0, 5, viz, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

    pdf.ln(3)
    pdf.titulo_seccion("15. CONVENCIONES DE CODIGO")
    convenciones = [
        ("Credenciales", "Leer del .env con python-dotenv", "Escribir passwords en el codigo"),
        ("Rutas",        "os.path.join('data','raw','sena')", "'data\\\\raw\\\\sena' hardcodeado"),
        ("Red",          "try/except con reintentos automaticos","Dejar que el script falle"),
        ("Comentarios",  "Explicar el POR QUE (no el QUE obvio)","# suma 1 a x"),
        ("Funciones",    "Una funcion = una responsabilidad", "Funciones de 100 lineas"),
        ("Nombres",      "tasa_desocupacion, extraer_sena()", "td, func1(), datos2"),
        ("Datos crudos", "data/raw/ es INMUTABLE",            "Sobrescribir archivos originales"),
    ]
    pdf.fila_tabla(["Regla","Correcto","Evitar"],
                   [38,76,76], fondo=AZUL_OSCURO, negrita=True)
    for i, c in enumerate(convenciones):
        pdf.fila_tabla(c, [38,76,76], fondo=GRIS_FONDO if i%2==0 else BLANCO)


# ── Main ──────────────────────────────────────────────────────────
def generar_pdf():
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(10, 16, 10)

    # Portada
    pdf.add_page()
    portada(pdf)

    # Contenido
    pagina_contexto(pdf)
    pagina_arquitectura(pdf)
    pagina_fuentes(pdf)
    pagina_hecho(pdf)
    pagina_modelo(pdf)
    pagina_estado(pdf)
    pagina_powerbi(pdf)

    pdf.output(RUTA_PDF)
    print(f"PDF generado: {RUTA_PDF}")


if __name__ == "__main__":
    generar_pdf()
