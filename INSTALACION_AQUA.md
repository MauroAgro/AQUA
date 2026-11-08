# 💧 AQUA — Autonomous Query & Utility Assistant

Guía de instalación y puesta en marcha en **Windows 11**.

AQUA es una versión del asistente **JARVIS** renombrada completamente a **AQUA**, adaptada para recibir comandos por **WhatsApp** además de Telegram y voz.

---

## 1. Qué se incluye

Esta carpeta contiene todo el código listo para usar en el PC destino:

| Archivo | Qué hace |
|---------|----------|
| `aqua.py` | Programa principal de AQUA (ventana, voz, detección de órdenes, ejecución). |
| `aqua_system.py` | Información de hardware (CPU, GPU, RAM, discos, temperaturas, red). |
| `configuracion.py` | Menú de configuración inicial (se ejecuta la primera vez). |
| `whatsapp.py` / `wa_send.py` | Enviar mensajes por WhatsApp Web (Selenium + Chrome). |
| `whatsapp_comandos.py` | **Nuevo:** recibir y ejecutar comandos que tú envíes por WhatsApp. |
| `telegram_bot.py` | Control remoto por Telegram (se conserva como respaldo). |
| Módulos extra | Calendario, correo, archivos, notas, clima, fútbol, juegos, etc. |

---

## 2. Requisitos en el PC con Windows 11

Instala esto **antes** de ejecutar AQUA:

| Requisito | Cómo conseguirlo |
|-----------|------------------|
| **Python 3.10 o superior** | https://www.python.org/downloads/ <br>⚠️ Al instalar, marca la casilla **"Add Python to PATH"**. |
| **Ollama** | https://ollama.com <br>Después, descarga los modelos de IA (ver paso 5). |
| **Google Chrome** | https://www.google.com/chrome/ (necesario para WhatsApp Web). |
| **ChromeDriver** | Debe coincidir con la versión de Chrome instalada. <br>Descarga desde: https://googlechromelabs.github.io/chrome-for-testing/ |

---

## 3. Pasos de instalación (en orden)

### Paso A — Descargar el proyecto
Copia esta carpeta completa (`AQUA`) al PC con Windows 11 donde quieres que viva el asistente.

### Paso B — Instalar dependencias de Python
Abre una terminal (PowerShell o CMD) dentro de la carpeta `AQUA` y ejecuta:

```powershell
python -m pip install -r requirements.txt
```

### Paso C — Instalar Ollama y los modelos
1. Instala Ollama desde https://ollama.com.
2. Abre una terminal y ejecuta:

```powershell
ollama pull qwen3:8b
ollama pull qwen2.5-coder:7b
```

(Opcional) Si quieres análisis de imágenes por IA:
```powershell
ollama pull llava
```

### Paso D — Preparar WhatsApp Web (Chrome + perfil)
Dentro de la carpeta `AQUA`, crea estas carpetas vacías (si no existen):

```
chrome-win64/       ← pon aquí chrome.exe
chromedriver-win64/ ← pon aquí chromedriver.exe
wa_profile/         ← aquí se guarda la sesión de WhatsApp Web
```

- `chrome.exe`: el ejecutable de Google Chrome.
- `chromedriver.exe`: descárgalo de la web de Chrome for Testing (versión que coincida con tu Chrome).
- `wa_profile`: se llena sola la primera vez que vincules WhatsApp.

### Paso E — Arrancar AQUA por primera vez
```powershell
python aqua.py
```

Aparecerá un menú de configuración que te preguntará:
- Tu nombre y ciudad.
- Si quieres activar Telegram (opcional).
- Qué modelos de IA usar (los que bajaste en el Paso C).
- Qué módulos activar.

Todo se guarda en `config.json`. La próxima vez, AQUA arranca directo.

---

## 4. Control por WhatsApp (enviar comandos a AQUA)

AQUA incluye el módulo `whatsapp_comandos.py` que lee tus mensajes de WhatsApp y los ejecuta como órdenes.

### Cómo configurarlo
1. Abre `config.json` (se crea tras el primer arranque).
2. Añade estas dos claves:

```json
"whatsapp_contacto_autorizado": "+34600000000",
"whatsapp_polling_segundos": 30
```

- Reemplaza `+34600000000` por tu propio número de teléfono (con código de país) o por el nombre del contacto como aparece en WhatsApp.
- `whatsapp_polling_segundos`: cada cuántos segundos AQUA revisa si hay mensajes nuevos (30 es un buen valor).

3. Guarda `config.json` y reinicia `aqua.py`.

### Cómo usarlo
Desde tu móvil, abre WhatsApp y envía un mensaje al número/configurado (o al contacto guardado en el PC). AQUA lo recibirá, ejecutará la orden en el PC y te responderá por WhatsApp.

Ejemplos de órdenes que entenderá:
- `"¿qué temperatura hace?"`
- `"información de mi pc"`
- `"pon una alarma a las 8 de la mañana"`
- `"apunta comprar pan"`
- `"abre el bloc de notas"`
- `"cuánto es 8 por 5"`

### ⚠️ Limitaciones importantes de WhatsApp
- **WhatsApp SIEMPRE requiere un número de teléfono.** No existe forma de usar WhatsApp sin una línea telefónica válida asociada a una cuenta. Si no tienes número, no podrás usar este canal; usa Telegram en su lugar (ya incluido).
- La primera vez, debes **vincular WhatsApp Web**: al abrir AQUA, se abrirá Chrome con un código QR. Escanéalo con la app de WhatsApp de tu móvil (Ajustes → Dispositivos vinculados → Vincular dispositivo).
- Debes dejar el PC **encendido y con Chrome funcionando** para que AQUA pueda leer tus mensajes. Si cierras Chrome o apagas el PC, WhatsApp deja de funcionar.
- WhatsApp puede detectar automatización y, en casos raros, pedir que vuelvas a escanear el QR o bloquear temporalmente la sesión.

---

## 5. Consultar datos del PC desde otra máquina

AQUA puede generar un reporte del sistema y guardarlo en un archivo para que tú lo consultes desde cualquier sitio.

Cuando estés hablando con AQUA (voz, Telegram o WhatsApp), pídele:

> **"Guarda un reporte de mi pc"**

o usa la opción de voz (tecla F9) y dile lo mismo. AQUA escribirá un archivo `reporte_pc.txt` en el escritorio con información del procesador, memoria, discos, temperaturas y red.

Luego puedes:
- Copiar y pegar el contenido de ese archivo en esta conversación para que yo lo analice.
- O enviarme el archivo directamente.

---

## 6. Nombre del asistente

Todas las referencias internas ya pasaron de **JARVIS** a **AQUA**:
- Mensaje del sistema: *"Eres AQUA, el asistente personal de ..."*
- Ventana de la aplicación: *AQUA // SYSTEM ONLINE*
- Detección de órdenes: *cierra aqua, adiós aqua*, etc.

Si en el futuro quieres cambiarlo de nuevo, edita `configuracion.py` o `aqua.py` y reemplaza "AQUA" por el nombre que desees.

---

## 7. Solución rápida de problemas

| Problema | Solución |
|----------|----------|
| `python` no reconocido | Reinstala Python marcando "Add Python to PATH". |
| `ollama` no reconocido | Instala Ollama desde https://ollama.com y reinicia la terminal. |
| WhatsApp pide QR | Escanea con el móvil y vincula el dispositivo. |
| WhatsApp dice sesión caducada | Vuelve a escanear el QR; borra el contenido de `wa_profile/` y empieza de nuevo. |
| AQUA no responde por voz | Asegúrate de tener activado el módulo de voz en la configuración y Piper instalado. |

---

## 8. Soporte

Si algo no funciona, copia el texto del error (o una captura de pantalla) y compártelo aquí. Con eso puedo decirte exactamente qué editar.
