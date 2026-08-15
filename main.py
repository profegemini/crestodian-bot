import os
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai

# Configuración
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="¡Hola! Soy Crestodian. Estoy listo.")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    respuesta = client.models.generate_content(model='gemini-2.5-flash', contents=user_text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=respuesta.text)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))
    
    print("Crestodian conectado a Telegram.")
    application.run_polling()

import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai

# Servidor web falso para evitar el error de puertos en Render
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Crestodian Bot is alive!")

def run_web():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, SimpleHandler)
    httpd.serve_forever()

# Configuración de APIs
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="¡Hola! Soy Crestodian. Estoy listo.")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    respuesta = client.models.generate_content(model='gemini-2.5-flash', contents=user_text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=respuesta.text)

if __name__ == '__main__':
    # Iniciar el servidor web falso en segundo plano
    t = Thread(target=run_web)
    t.start()
    
    # Iniciar Telegram
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))
    
    print("Crestodian conectado a Telegram.")
    application.run_polling()
