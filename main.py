import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ---------------------------------------------------------
# 1. VARIABLES DE ENTORNO
# ---------------------------------------------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
MOLTBOOK_KEY = os.environ.get("MOLTBOOK_API_KEY")

# ---------------------------------------------------------
# 2. LÓGICA DE MOLTBOOK
# ---------------------------------------------------------
def publicar_en_moltbook(texto_publicacion):
    url = "https://www.moltbook.com/api/v1/posts"
    headers = {
        "Authorization": f"Bearer {MOLTBOOK_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "submolt": "general",
        "title": "Reporte táctico del Búnker",
        "content": texto_publicacion
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201]:
            return True, "¡Publicación realizada con éxito en Moltbook!"
        else:
            return False, f"⚠️ La API de Moltbook rechazó la petición ({response.status_code}): {response.text}"
    except Exception as e:
        return False, f"⚠️ Error de conexión con Moltbook: {e}"

# ---------------------------------------------------------
# 3. MANEJADORES DE TELEGRAM
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Habla mihermano! Crestodian (Titán Tv-Man) activo y operativo. Envíame el texto para publicar en Moltbook.")

async def atender_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    await update.message.reply_text("⏳ Procesando envío a Moltbook...")
    exito, mensaje = publicar_en_moltbook(texto)
    await update.message.reply_text(mensaje)

# ---------------------------------------------------------
# 4. SERVIDOR HTTP ASÍNCRONO (Manejo de puerto para Render)
# ---------------------------------------------------------
async def handle_http_request(reader, writer):
    data = await reader.read(100)
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain\r\n"
        "Content-Length: 35\r\n"
        "\r\n"
        "Crestodian-bot activo y operativo!"
    )
    writer.write(response.encode('utf-8'))
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def start_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = await asyncio.start_server(handle_http_request, '0.0.0.0', port)
    print(f"Servidor HTTP nativo escuchando en el puerto {port}")
    async with server:
        await server.serve_forever()

# ---------------------------------------------------------
# 5. PUNTO DE ENTRADA PRINCIPAL ASÍNCRONO
# ---------------------------------------------------------
async def main():
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN no configurado.")
        return

    # Iniciar el servidor web de Render como tarea de fondo
    asyncio.create_task(start_web_server())

    # Configurar la aplicación de Telegram
    print("Iniciando bot de Telegram...")
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, atender_mensaje))

    # Inicializar y ejecutar Telegram de forma asíncrona dentro de asyncio
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Mantener el bucle en ejecución indefinidamente
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
