import sys
import os
import time
import glob
import shutil
from datetime import datetime
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

load_dotenv()

URL_FILCO_BASE = "https://filco.mintrabajo.gov.co"
RUTA_SALIDA    = os.path.join("data", "raw", "filco")
RUTA_TEMP      = os.path.join(RUTA_SALIDA, "_temp_downloads")

ESPERA_CARGA    = 20
ESPERA_DESCARGA = 90
PAUSA_NAV       = 3

SECCIONES_OBJETIVO = ["informalidad", "formalidad", "afiliacion", "seguridad social"]


def crear_driver(ruta_descargas):
    opciones = Options()
    opciones.add_argument("--headless=new")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("--disable-dev-shm-usage")
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--window-size=1920,1080")
    opciones.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    opciones.add_experimental_option("prefs", {
        "download.default_directory": os.path.abspath(ruta_descargas),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    })
    return webdriver.Chrome(options=opciones)


def esperar_descarga(ruta, timeout=ESPERA_DESCARGA):
    inicio = time.time()
    while time.time() - inicio < timeout:
        parciales = glob.glob(os.path.join(ruta, "*.crdownload"))
        completos = [f for f in os.listdir(ruta) if not f.endswith(".crdownload") and not f.startswith("_")]
        if completos and not parciales:
            return completos
        time.sleep(2)
    return []


def buscar_boton_descarga(driver, wait):
    selectores = [
        "button[title*='xport']", "button[title*='escarga']",
        "a[href*='download']", "a[href*='export']",
        ".export-button", ".download-btn", "[data-export]",
        "//button[contains(text(),'Exportar')]",
        "//button[contains(text(),'Descargar')]",
        "//a[contains(text(),'Excel')]",
        "//a[contains(text(),'CSV')]",
    ]
    for sel in selectores:
        try:
            elem = driver.find_element(By.XPATH, sel) if sel.startswith("//") else driver.find_element(By.CSS_SELECTOR, sel)
            elem.click()
            return True
        except (NoSuchElementException, StaleElementReferenceException):
            continue
    return False


def descargar_seccion(driver, url, nombre_seccion):
    os.makedirs(RUTA_TEMP, exist_ok=True)
    for f in glob.glob(os.path.join(RUTA_TEMP, "*")):
        os.remove(f)

    wait = WebDriverWait(driver, ESPERA_CARGA)
    print(f"  Navegando: {url}")
    driver.get(url)
    time.sleep(PAUSA_NAV)

    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    except TimeoutException:
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "chart")))
        except TimeoutException:
            pass

    encontrado = buscar_boton_descarga(driver, wait)
    if not encontrado:
        print(f"    ⚠ No se encontró botón de descarga en {nombre_seccion}")

    archivos = esperar_descarga(RUTA_TEMP, timeout=30 if not encontrado else ESPERA_DESCARGA)
    destinos = []
    for arch in archivos:
        destino = os.path.join(RUTA_SALIDA, f"filco_{nombre_seccion}_{arch}")
        shutil.move(os.path.join(RUTA_TEMP, arch), destino)
        destinos.append(destino)
        print(f"    ✓ {os.path.basename(destino)} ({os.path.getsize(destino)/1024:.0f} KB)")
    return destinos


def extraer_filco_requests():
    import requests
    endpoints = [
        f"{URL_FILCO_BASE}/api/informalidad/export?format=csv",
        f"{URL_FILCO_BASE}/api/formalidad/export?format=csv",
        f"{URL_FILCO_BASE}/export/informalidad.xlsx",
        f"{URL_FILCO_BASE}/export/formalidad.xlsx",
    ]
    descargados = []
    for url in endpoints:
        try:
            r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0", "Referer": URL_FILCO_BASE})
            if r.status_code == 200 and len(r.content) > 1000:
                ext    = ".xlsx" if "xlsx" in url else ".csv"
                nombre = f"filco_{url.split('/')[-1].split('?')[0]}"
                if not nombre.endswith(ext):
                    nombre += ext
                ruta = os.path.join(RUTA_SALIDA, nombre)
                with open(ruta, "wb") as f:
                    f.write(r.content)
                print(f"    ✓ (directo) {nombre} ({len(r.content)/1024:.0f} KB)")
                descargados.append(ruta)
        except Exception:
            pass
    return len(descargados) > 0


def _limpiar_temp():
    if os.path.exists(RUTA_TEMP):
        shutil.rmtree(RUTA_TEMP, ignore_errors=True)


def _mostrar_instrucciones_manuales():
    print("""
╔══════════════════════════════════════════════════════╗
║  DESCARGA MANUAL — FILCO MinTrabajo                  ║
╠══════════════════════════════════════════════════════╣
║  1. Ir a: filco.mintrabajo.gov.co                    ║
║  2. Sección: Informalidad → botón Exportar/Excel     ║
║  3. Sección: Formalidad → botón Exportar/Excel       ║
║  4. Sección: Afiliación seguridad social             ║
║  5. Guardar archivos en: data/raw/filco/             ║
║  Formatos aceptados: .xlsx / .csv                    ║
╚══════════════════════════════════════════════════════╝
""")


def extraer_filco():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando extracción FILCO (Selenium)...\n")
    os.makedirs(RUTA_SALIDA, exist_ok=True)

    print("  Intentando descarga directa (sin Selenium)...")
    if extraer_filco_requests():
        print("  ✓ Descarga directa exitosa.")
        _limpiar_temp()
        return

    print("  Descarga directa no disponible. Usando Selenium...\n")
    driver = crear_driver(RUTA_TEMP)
    total  = []

    try:
        for seccion in SECCIONES_OBJETIVO:
            archivos = descargar_seccion(driver, f"{URL_FILCO_BASE}/{seccion}", seccion.replace(" ", "_"))
            total.extend(archivos)
            time.sleep(PAUSA_NAV)
    finally:
        driver.quit()
        _limpiar_temp()

    print(f"\n{'─'*55}")
    if total:
        print(f"  ✓ Total archivos FILCO : {len(total)}")
        for ruta in total:
            print(f"    {os.path.basename(ruta)}")
    else:
        _mostrar_instrucciones_manuales()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Extracción FILCO completada.")


if __name__ == "__main__":
    extraer_filco()
