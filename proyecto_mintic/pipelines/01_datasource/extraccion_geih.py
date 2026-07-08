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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

load_dotenv()

CATALOGOS = {
    "2024": "https://microdatos.dane.gov.co/index.php/catalog/819/get-microdata",
    "2025": "https://microdatos.dane.gov.co/index.php/catalog/853/get-microdata",
}

RUTA_SALIDA = os.path.join("data", "raw", "geih")
RUTA_TEMP   = os.path.join(RUTA_SALIDA, "_temp_downloads")

ESPERA_CARGA     = 20
ESPERA_DESCARGA  = 180
PAUSA_ENTRE_URLS = 3

MODULOS_OBJETIVO = ["caracteristicas", "ocupados", "desocupados", "inactivos", "fuerza de trabajo", "vivienda"]


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
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True,
    })
    return webdriver.Chrome(options=opciones)


def esperar_descarga(ruta_destino, timeout=ESPERA_DESCARGA):
    inicio = time.time()
    while time.time() - inicio < timeout:
        parciales = glob.glob(os.path.join(ruta_destino, "*.crdownload"))
        archivos  = [f for f in os.listdir(ruta_destino) if not f.endswith(".crdownload") and not f.startswith("_")]
        if not parciales and archivos:
            return True
        time.sleep(2)
    return False


def es_modulo_objetivo(nombre):
    return any(mod in nombre.lower() for mod in MODULOS_OBJETIVO)


def aceptar_terminos(driver, wait):
    try:
        checkbox = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='checkbox']")))
        if not checkbox.is_selected():
            checkbox.click()
            time.sleep(0.5)
        boton = driver.find_element(
            By.XPATH,
            "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'continuar') or "
            "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'continue') or "
            "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'accept')]",
        )
        boton.click()
        print("    Términos aceptados.")
        time.sleep(2)
    except (TimeoutException, NoSuchElementException):
        pass


def obtener_enlaces_descarga(driver, wait):
    try:
        wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "a[href*='.zip'], a[href*='.csv'], a[href*='.sav'], a[href*='.dta'], a[href*='download']"
        )))
    except TimeoutException:
        pass
    enlaces = driver.find_elements(
        By.CSS_SELECTOR,
        "a[href*='.zip'], a[href*='.csv'], a[href*='.sav'], a[href*='.dta'], a[href*='/download']",
    )
    return [
        {"nombre": e.text.strip() or e.get_attribute("title") or "", "url": e.get_attribute("href") or ""}
        for e in enlaces if e.get_attribute("href")
    ]


def _buscar_enlaces_alternativo(driver):
    return [
        {"nombre": tag.text.strip() or href.split("/")[-1], "url": href}
        for tag in driver.find_elements(By.TAG_NAME, "a")
        if any(ext in (href := tag.get_attribute("href") or "") for ext in [".zip", ".csv", ".sav", ".dta"])
    ]


def _nombre_seguro(nombre, anio):
    nombre_limpio = "".join(c if c.isalnum() or c in "._- " else "_" for c in nombre).strip().replace(" ", "_")[:80]
    if not nombre_limpio:
        nombre_limpio = f"geih_{anio}_{int(time.time())}"
    if not any(nombre_limpio.lower().endswith(e) for e in [".zip", ".csv", ".sav", ".dta"]):
        nombre_limpio += ".zip"
    return nombre_limpio


def descargar_archivos_anio(anio, url_catalogo):
    ruta_anio = os.path.join(RUTA_SALIDA, anio)
    os.makedirs(ruta_anio, exist_ok=True)
    os.makedirs(RUTA_TEMP,  exist_ok=True)
    for f in glob.glob(os.path.join(RUTA_TEMP, "*")):
        os.remove(f)

    driver = crear_driver(RUTA_TEMP)
    wait   = WebDriverWait(driver, ESPERA_CARGA)
    descargados = 0

    try:
        print(f"  Navegando a: {url_catalogo}")
        driver.get(url_catalogo)
        time.sleep(3)

        aceptar_terminos(driver, wait)

        for texto_tab in ["archivos de datos", "data files", "files"]:
            try:
                driver.find_element(
                    By.XPATH,
                    f"//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{texto_tab}')]",
                ).click()
                time.sleep(2)
                break
            except NoSuchElementException:
                continue

        enlaces = obtener_enlaces_descarga(driver, wait)
        print(f"  Enlaces encontrados: {len(enlaces)}")
        if not enlaces:
            print("  ⚠ No se encontraron enlaces. Intentando estrategia alternativa...")
            enlaces = _buscar_enlaces_alternativo(driver)
            print(f"  Enlaces (alt): {len(enlaces)}")

        for item in enlaces:
            if not es_modulo_objetivo(item["nombre"]):
                continue

            nombre_archivo = _nombre_seguro(item["nombre"], anio)
            ruta_final     = os.path.join(ruta_anio, nombre_archivo)

            if os.path.exists(ruta_final):
                print(f"    ⏭ Ya existe: {nombre_archivo}")
                descargados += 1
                continue

            print(f"    ↓ Descargando: {item['nombre'][:60]} ...", end="", flush=True)
            for f in glob.glob(os.path.join(RUTA_TEMP, "*")):
                os.remove(f)

            try:
                driver.get(item["url"])
                if esperar_descarga(RUTA_TEMP):
                    archivos_temp = [f for f in os.listdir(RUTA_TEMP) if not f.endswith(".crdownload") and not f.startswith("_")]
                    for arch in archivos_temp:
                        shutil.move(os.path.join(RUTA_TEMP, arch), os.path.join(ruta_anio, arch))
                    tam_mb = sum(os.path.getsize(os.path.join(ruta_anio, a)) for a in archivos_temp) / (1024 * 1024)
                    print(f" ✓ ({tam_mb:.1f} MB)")
                    descargados += 1
                else:
                    print(" ✗ Timeout")
            except Exception as e:
                print(f" ✗ Error: {e}")

            time.sleep(PAUSA_ENTRE_URLS)

    finally:
        driver.quit()
        if os.path.exists(RUTA_TEMP):
            shutil.rmtree(RUTA_TEMP, ignore_errors=True)

    return descargados


def _mostrar_instrucciones_manuales():
    print("""
╔══════════════════════════════════════════════════════╗
║  DESCARGA MANUAL — Portal DANE requiere interacción  ║
╠══════════════════════════════════════════════════════╣
║  1. Ir a:                                            ║
║     2024 → microdatos.dane.gov.co/catalog/819        ║
║     2025 → microdatos.dane.gov.co/catalog/853        ║
║  2. Clic en pestaña "Archivos de datos"              ║
║  3. Aceptar términos de uso                          ║
║  4. Descargar módulos:                               ║
║     - Características generales                      ║
║     - Ocupados                                       ║
║     - Desocupados / Inactivos                        ║
║  5. Guardar en: data/raw/geih/2024/  y  .../2025/    ║
╚══════════════════════════════════════════════════════╝
""")


def extraer_geih():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando extracción GEIH (Selenium)...")
    print(f"  Módulos objetivo: {MODULOS_OBJETIVO}\n")

    os.makedirs(RUTA_SALIDA, exist_ok=True)
    total = 0

    for anio, url in CATALOGOS.items():
        print(f"\n{'─'*55}\n  GEIH {anio}\n{'─'*55}")
        n = descargar_archivos_anio(anio, url)
        total += n
        print(f"  → {n} archivo(s) procesados para {anio}")

    print(f"\n{'─'*55}")
    print(f"  ✓ Total archivos : {total}")
    print(f"  ✓ Carpeta        : {RUTA_SALIDA}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Extracción GEIH completada.")

    if total == 0:
        _mostrar_instrucciones_manuales()


if __name__ == "__main__":
    extraer_geih()
