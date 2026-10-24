import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import requests

# 1. Servidor HTTP en segundo plano para satisfacer el puerto de Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Crestodian-bot activo y operativo!")
        
    def log_message(self, format, *args):
        return

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"Servidor web activo en puerto {port}")
    server.serve_forever()

# Lanzar el servidor web de fondo de inmediato
threading.Thread(target=run_server, daemon=True).start()

# 2. Configuración y credenciales
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
MOLTBOOK_KEY = os.environ.get("MOLTBOOK_API_KEY")

# 3. Lógica de Moltbook
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

# 4. Manejadores de Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Habla mihermano! Crestodian (Titán Tv-Man) operativo. Envíame el texto para publicar en Moltbook.")

async def atender_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    await update.message.reply_text("⏳ Procesando envío a Moltbook...")
    exito, mensaje = publicar_en_moltbook(texto)
    await update.message.reply_text(mensaje)

# 5. Ejecución principal de Telegram
def main():
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN no configurado.")
        return

    print("Bot iniciando en Telegram...")
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, atender_mensaje))
    
    application.run_polling()

if __name__ == "__main__":
    main()
