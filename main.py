import os
import threading
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
# 1. SERVIDOR WEB PARA RENDER (Inicia de primero)
# ---------------------------------------------------------
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Crestodian-bot activo y operativo!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"Servidor web activo en puerto {port}")
    server.serve_forever()

# Iniciar servidor web de fondo INMEDIATAMENTE al arrancar el script
threading.Thread(target=run_web_server, daemon=True).start()

# ---------------------------------------------------------
# 2. VARIABLES DE ENTORNO
# ---------------------------------------------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
MOLTBOOK_KEY = os.environ.get("MOLTBOOK_API_KEY")

# ---------------------------------------------------------
# 3. LÓGICA DE MOLTBOOK
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
            return False, f"⚠️ La API de Moltbook rechazó la petición (Código {response.status_code}): {response.text}"
    except Exception as e:
        return False, f"⚠️ Error de conexión con Moltbook: {e}"

# ---------------------------------------------------------
# 4. BOT DE TELEGRAM
# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Habla mihermano! Crestodian (Titán Tv-Man) reportándose. Envíame lo que quieras publicar en Moltbook.")

async def atender_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    await update.message.reply_text(" Procesando y enviando a Moltbook...")
    
    exito, mensaje = publicar_en_moltbook(texto)
    await update.message.reply_text(mensaje)

# ---------------------------------------------------------
# 5. INICIALIZACIÓN DE TELEGRAM (Al final)
# ---------------------------------------------------------
if __name__ == '__main__':
    print("Bot iniciando en Telegram...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, atender_mensaje))
    
    # Esto bloquea la ejecución, pero el servidor web YA inició arriba
    app.run_polling()
