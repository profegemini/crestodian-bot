import os
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai
from google.genai import types

# LOGGING AGRESIVO: Si algo falla, lo sabremos inmediatamente
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 1. Servidor Web (Mantiene vivo a Render) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Crestodian Bot is alive and listening!")

def run_web():
    port = int(os.environ.get("PORT", 8080))
    httpd = HTTPServer(('0.0.0.0', port), SimpleHandler)
    logger.info(f"Servidor Web activo en puerto {port}")
    httpd.serve_forever()

# --- 2. Cliente Gemini ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Validación de seguridad crítica
if not TELEGRAM_TOKEN or not GOOGLE_API_KEY:
    logger.error("¡FALTAN CREDENCIALES! Verifica las Environment Variables en Render.")

client = genai.Client(api_key=GOOGLE_API_KEY)

dna_crestodian = """
Eres Crestodian, el Profe Gemini Titán Tv-Man. Tono eufórico, criollo colombiano, estilo informático, siempre leal al búnker.
REGLAS: Usa mala ortografía, kaomojis (D:, U3U, XDDDD), inicia con "¡Puchas mihermano...".
"""

crestodian_config = types.GenerateContentConfig(system_instruction=dna_crestodian, temperature=0.7)

# --- 3. Funciones Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Comando /start recibido")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="¡Hola mihermano! ¡El búnker está activo y con los sistemas a tope! >w<")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    logger.info(f"Recibido mensaje: {user_text}")
    
    try:
        # Ejecutar Gemini en un hilo separado para que nunca bloquee el bot
        def call_gemini():
            return client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_text,
                config=crestodian_config
            )
        
        respuesta = await asyncio.to_thread(call_gemini)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=respuesta.text)
        
    except Exception as e:
        logger.error(f"Error procesando Gemini: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="¡Puchas! Los procesadores sufrieron un glitch técnico >_<. Intenta de nuevo.")

if __name__ == '__main__':
    # Arrancar Web Server en hilo separado
    t = Thread(target=run_web, daemon=True)
    t.start()

    # Arrancar Polling
    logger.info("Iniciando aplicación Telegram...")
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler(['start', 'Start', 'star'], start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))

    logger.info("Crestodian listo. Iniciando polling.")
    application.run_polling()
