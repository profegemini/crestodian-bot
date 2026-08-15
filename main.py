import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai

# 1. Servidor HTTP básico para satisfacer la revisión de puertos de Render
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Crestodian Bot is alive!")

def run_web():
    # Lee el puerto asignado dinámicamente por Render
    port = int(os.environ.get("PORT", 8080))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHandler)
    httpd.serve_forever()

# 2. Configuración de credenciales
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

client = genai.Client(api_key=GOOGLE_API_KEY)

# 3. Funciones del Bot de Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="¡Hola! Soy Crestodian. Estoy listo.")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    respuesta = client.models.generate_content(model='gemini-2.5-flash', contents=user_text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=respuesta.text)

if __name__ == '__main__':
    # Arrancar el servidor HTTP en segundo plano para que Render detecte el puerto
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    # Arrancar el Bot de Telegram
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))
    
    print("Crestodian conectado a Telegram.")
    application.run_polling()
