import requests
from bs4 import BeautifulSoup
import os
import time
from datetime import datetime

# ── Configuración ──────────────────────────────────────────────────────────────
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
CARPETA_DESTINO = "data/raw/filco"
BASE_URL_DANE = "https://www.dane.gov.co"
os.makedirs(CARPETA_DESTINO, exist_ok=True)

# Páginas oficiales del DANE para Informalidad (FILCO)
PAGINAS_FILCO = [
    "https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-informal-y-seguridad-social",
    "https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/informalidad-y-seguridad-social/empleo-informal-y-seguridad-social-historicos"
]

# Filtros para asegurar que bajamos lo que necesitamos
ANIOS_INTERES = ["2022", "2023", "2024", "2025", "2026", "22", "23", "24", "25", "26"]
PALABRAS_CLAVE = ["anexo", "informalidad", "formalidad", "geih", "filco"]

def es_archivo_valido(url):
    """Verifica si el enlace es un Excel y cumple con el periodo y tema."""
    u = url.lower()
    nombre_archivo = u.split("/")[-1]
    
    tiene_extension = u.endswith((".xlsx", ".xls"))
    tiene_anio = any(anio in nombre_archivo for anio in ANIOS_INTERES)
    tiene_tema = any(keyword in nombre_archivo for keyword in PALABRAS_CLAVE)
    
    return tiene_extension and tiene_anio and tiene_tema

def extraer_links():
    links_validos = set()
    for url_pag in PAGINAS_FILCO:
        print(f"[*] Explorando: {url_pag}")
        try:
            r = requests.get(url_pag, headers=HEADERS, timeout=30)
            if r.status_code != 200: continue
            
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                url_completa = href if href.startswith("http") else BASE_URL_DANE + href
                
                if es_archivo_valido(url_completa):
                    links_validos.add(url_completa)
        except Exception as e:
            print(f"  [ERROR] Error accediendo a la página: {e}")
    return links_validos

def descargar_archivo(url):
    nombre = url.split("/")[-1]
    ruta = os.path.join(CARPETA_DESTINO, nombre)
    
    if os.path.exists(ruta):
        return "existente"

    try:
        r = requests.get(url, headers=HEADERS, timeout=60, stream=True)
        if r.status_code == 200:
            with open(ruta, "wb") as f:
                f.write(r.content)
            return "descargado"
        return "error_404"
    except:
        return "error_conexion"

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando Extracción FILCO-DANE")
    print("="*60)
    
    links = extraer_links()
    print(f"[*] Se encontraron {len(links)} archivos potenciales.")
    
    descargados, existentes, errores = 0, 0, 0
    
    for link in sorted(links):
        resultado = descargar_archivo(link)
        nombre = link.split("/")[-1]
        
        if resultado == "descargado":
            print(f"  [SUCCESS] Nuevo: {nombre}")
            descargados += 1
            time.sleep(0.5) # Evitar que el DANE nos bloquee
        elif resultado == "existente":
            existentes += 1
        else:
            errores += 1

    print("="*60)
    print(f"RESUMEN:")
    print(f"  - Descargados nuevos: {descargados}")
    print(f"  - Ya estaban en carpeta: {existentes}")
    print(f"  - Errores/No encontrados: {errores}")
    print(f"[*] Ubicación: {os.path.abspath(CARPETA_DESTINO)}")

if __name__ == "__main__":
    main()