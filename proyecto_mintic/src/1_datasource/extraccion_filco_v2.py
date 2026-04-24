import os
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
URLS = [
    "https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/empleo-informal-y-seguridad-social",
    "https://www.dane.gov.co/index.php/estadisticas-por-tema/salud/informalidad-y-seguridad-social/empleo-informal-y-seguridad-social-historicos"
]

HEADERS = {
    "User-Agent": os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
}

RETRIES = int(os.getenv("RETRIES", 3))
RAW_PATH = os.path.join("data", "raw", "filco")

def asegurar_directorios():
    """Crea la estructura de carpetas si no existe."""
    if not os.path.exists(RAW_PATH):
        os.makedirs(RAW_PATH)
        print(f"Directorio creado: {RAW_PATH}")

def descargar_archivo(url, nombre_archivo):
    """Descarga un archivo con lógica de reintentos e inmutabilidad."""
    ruta_final = os.path.join(RAW_PATH, nombre_archivo)
    
    # Inmutabilidad: Si el archivo ya existe, omitir
    if os.path.exists(ruta_final):
        print(f"[-] El archivo ya existe, omitiendo: {nombre_archivo}")
        return True

    intentos = 0
    while intentos < RETRIES:
        try:
            print(f"[*] Descargando {nombre_archivo} (Intento {intentos + 1})...")
            response = requests.get(url, headers=HEADERS, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(ruta_final, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"[+] Descarga exitosa: {nombre_archivo}")
            return True
        except Exception as e:
            intentos += 1
            print(f"[!] Error al descargar {url}: {e}. Reintentando...")
            time.sleep(2)
    
    print(f"[ERROR] No se pudo descargar {nombre_archivo} después de {RETRIES} intentos.")
    return False

def extraer_enlaces_dane():
    """Explora las páginas del DANE y extrae enlaces de archivos 2022-2026."""
    enlaces_encontrados = []
    
    for url_base in URLS:
        print(f"[*] Explorando: {url_base}")
        try:
            response = requests.get(url_base, headers=HEADERS, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar todos los enlaces
            for a in soup.find_all('a', href=True):
                href = a['href']
                # Normalizar URL
                full_url = urljoin(url_base, href)
                
                # Filtro: .xls o .xlsx
                if full_url.endswith(('.xls', '.xlsx')):
                    # Extraer nombre del archivo desde la URL o el texto del enlace
                    nombre_archivo = full_url.split('/')[-1]
                    
                    # Filtro de años: 2022 a 2026
                    anios_validos = [str(anio) for anio in range(2022, 2027)]
                    if any(anio in nombre_archivo for anio in anios_validos):
                        enlaces_encontrados.append((full_url, nombre_archivo))
        
        except Exception as e:
            print(f"[!] Error explorando {url_base}: {e}")
            
    return list(set(enlaces_encontrados)) # Eliminar duplicados

def main():
    print("=== Iniciando Extracción de Datos FILCO (MinTIC 2026) ===")
    asegurar_directorios()
    
    archivos = extraer_enlaces_dane()
    print(f"[*] Se encontraron {len(archivos)} archivos potenciales.")
    
    exitos = 0
    for url, nombre in archivos:
        if descargar_archivo(url, nombre):
            exitos += 1
            
    print(f"\n=== Resumen de Extracción ===")
    print(f"Archivos encontrados: {len(archivos)}")
    print(f"Archivos procesados (descargados/omitidos): {exitos}")
    print("=========================================================")

if __name__ == "__main__":
    main()
