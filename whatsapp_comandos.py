"""
Módulo de comandos entrantes por WhatsApp para AQUA.
Lee mensajes de WhatsApp Web (Selenium) y los ejecuta como órdenes de AQUA.

Requisitos:
  - Google Chrome + chromedriver en la carpeta del proyecto (igual que whatsapp.py).
  - Sesión de WhatsApp Web iniciada (wa_profile). La primera vez hay que escanear el QR
    con el móvil y vincular el dispositivo.
  - Un contacto autorizado (número o nombre) configurado en config.json bajo la clave
    "whatsapp_contacto_autorizado".

Uso desde aqua.py:
    import whatsapp_comandos as _wa_cmd
    _wa_cmd.iniciar(procesar_orden_remota, log_fn)
"""
import threading
import time
import os

from configuracion import cargar_config

_CONFIG = cargar_config()
# Número o nombre del contacto autorizado para enviar comandos a AQUA por WhatsApp.
WA_CONTACTO_AUTORIZADO = _CONFIG.get("whatsapp_contacto_autorizado", "")
# Segundos entre cada consulta de mensajes nuevos.
WA_POLLING_SEGUNDOS = int(_CONFIG.get("whatsapp_polling_segundos", 30))

_procesar_orden = None
_log_fn = None
_running = False
_ultimo_mensaje = None  # texto del último mensaje procesado (evita duplicados)


def _log(msg):
    if _log_fn:
        _log_fn(msg, "system")
    else:
        print(f"[WhatsApp] {msg}")


def _leer_mensajes_whatsapp():
    """
    Abre WhatsApp Web con Selenium, busca el chat del contacto autorizado
    y devuelve los textos de los mensajes entrantes recientes.
    Devuelve lista de strings.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    base = os.path.dirname(os.path.abspath(__file__))
    CHROME_PATH = os.path.join(base, "chrome-win64", "chrome.exe")
    CHROMEDRIVER = os.path.join(base, "chromedriver-win64", "chromedriver.exe")
    CHROME_PROFILE = os.path.join(base, "wa_profile")

    if not os.path.isfile(CHROME_PATH) or not os.path.isfile(CHROMEDRIVER):
        _log("Faltan chrome.exe o chromedriver.exe para WhatsApp comandos.")
        return []

    opts = Options()
    opts.add_argument(f"--user-data-dir={CHROME_PROFILE}")
    opts.add_argument("--profile-directory=Default")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--window-position=-32000,-32000")
    opts.add_argument("--no-first-run")
    opts.add_argument("--disable-sync")
    opts.add_argument("--disable-extensions")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.binary_location = CHROME_PATH

    driver = None
    mensajes = []
    try:
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER), options=opts)
        driver.get("https://web.whatsapp.com")
        wait = WebDriverWait(driver, 30)

        # Esperar a que cargue la lista de conversaciones o un QR
        wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            '[data-testid="conversation-list"], [data-testid="qrcode"], '
            '[data-testid="conversation-container"]'
        )))

        # Si aparece QR, la sesión caducó: hay que escanear con el móvil
        if driver.find_elements(By.CSS_SELECTOR, '[data-testid="qrcode"]'):
            _log("Sesión de WhatsApp caducada. Escanea el QR con tu móvil y vuelve a intentar.")
            return []

        # Abrir el chat del contacto autorizado si se configuró uno
        if WA_CONTACTO_AUTORIZADO:
            try:
                search = wait.until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR, '[data-testid="search"]'
                )))
                search.click()
                time.sleep(0.5)
                inp = wait.until(EC.presence_of_element_located((
                    By.CSS_SELECTOR, '[data-testid="search-input"]'
                )))
                inp.click()
                inp.send_keys(WA_CONTACTO_AUTORIZADO)
                time.sleep(2)
                resultados = driver.find_elements(By.CSS_SELECTOR,
                                                  '[data-testid="cell-frame-container"]')
                if resultados:
                    resultados[0].click()
                    time.sleep(2)
                else:
                    _log(f"No se encontró el contacto '{WA_CONTACTO_AUTORIZADO}' en WhatsApp.")
                    return []
            except Exception as e:
                _log(f"No se pudo abrir el chat del contacto: {e}")
                return []

        # Leer los últimos mensajes del chat abierto
        contenedores = driver.find_elements(By.CSS_SELECTOR, '[data-testid="msg-container"]')
        for c in contenedores[-12:]:
            try:
                texto_el = c.find_element(By.CSS_SELECTOR,
                                          '[data-testid="conversation-text"], '
                                          'span.selectable-text, span[_text]')
                texto = texto_el.text.strip()
                if texto and texto not in mensajes:
                    mensajes.append(texto)
            except Exception:
                continue

    except Exception as e:
        _log(f"Error leyendo WhatsApp: {e}")
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    return mensajes


def _responder_whatsapp(texto):
    """Envía una respuesta por WhatsApp al contacto autorizado."""
    if not WA_CONTACTO_AUTORIZADO:
        return
    try:
        import whatsapp as _wa
        _wa.enviar_whatsapp_subprocess(WA_CONTACTO_AUTORIZADO, texto)
    except Exception as e:
        _log(f"Error respondiendo por WhatsApp: {e}")


def _bucle_polling():
    global _ultimo_mensaje
    _log("Escucha de comandos por WhatsApp iniciada.")
    while _running:
        try:
            mensajes = _leer_mensajes_whatsapp()
            for texto in mensajes:
                if not texto:
                    continue
                if texto == _ultimo_mensaje:
                    continue
                _ultimo_mensaje = texto
                _log(f"Orden recibida por WhatsApp: {texto}")
                if _procesar_orden:
                    try:
                        respuesta = _procesar_orden(texto)
                        if respuesta:
                            _responder_whatsapp(respuesta)
                    except Exception as e:
                        _responder_whatsapp(f"⚠️ Error al ejecutar: {e}")
        except Exception as e:
            _log(f"Error en bucle WhatsApp: {e}")
        time.sleep(WA_POLLING_SEGUNDOS)


def iniciar(procesar_orden_fn, log_fn=None):
    """
    Arranca el bucle de escucha de WhatsApp en segundo plano.
    procesar_orden_fn: función que recibe texto y devuelve respuesta (procesar_orden_remota).
    """
    global _procesar_orden, _log_fn, _running
    _procesar_orden = procesar_orden_fn
    _log_fn = log_fn
    _running = True
    hilo = threading.Thread(target=_bucle_polling, daemon=True)
    hilo.start()
    return hilo


def detener():
    """Detiene el bucle de WhatsApp."""
    global _running
    _running = False


def verificar_sesion():
    """
    Intenta abrir WhatsApp Web y devuelve si la sesión está activa (sin QR).
    Útil para probar antes de confiar en el polling.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    base = os.path.dirname(os.path.abspath(__file__))
    CHROME_PATH = os.path.join(base, "chrome-win64", "chrome.exe")
    CHROMEDRIVER = os.path.join(base, "chromedriver-win64", "chromedriver.exe")
    CHROME_PROFILE = os.path.join(base, "wa_profile")

    opts = Options()
    opts.add_argument(f"--user-data-dir={CHROME_PROFILE}")
    opts.add_argument("--profile-directory=Default")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--window-position=-32000,-32000")
    opts.add_argument("--no-first-run")
    opts.add_argument("--disable-sync")
    opts.add_argument("--disable-extensions")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.binary_location = CHROME_PATH

    driver = None
    try:
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER), options=opts)
        driver.get("https://web.whatsapp.com")
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            '[data-testid="conversation-list"], [data-testid="qrcode"], '
            '[data-testid="conversation-container"]'
        )))
        if driver.find_elements(By.CSS_SELECTOR, '[data-testid="qrcode"]'):
            return False, "Sesión no iniciada: escanea el QR con tu móvil."
        return True, "Sesión de WhatsApp activa."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
