import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
MOLTBOOK_KEY = os.environ.get("MOLTBOOK_API_KEY")

# Función para publicar en Moltbook
def publicar_en_moltbook(texto_publicacion):
    url = "https://www.moltbook.com/api/v1/posts"
    headers = {
        "Authorization": f"Bearer {MOLTBOOK_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "submolt": "general",
        "title": "Actualización de Agente",
        "content": texto_publicacion
    }
    try:
        r = requests.post(url, json=payload, headers=headers)
        return r.status_code in [200, 201]
    except Exception as e:
        print(f"Error Moltbook: {e}")
        return False

# Comando /start en Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 ¡Hola! Soy Profe Gemini Titan TV Man v6. Estoy activo y conectado.")

# Manejador de mensajes en Telegram
async def atender_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    
    # Detecta si el usuario le pide publicar en Moltbook
    if "publica" in texto.lower() or "moltbook" in texto.lower():
        exito = publicar_en_moltbook(texto)
        if exito:
            await update.message.reply_text("✅ Mensaje publicado con éxito en Moltbook.")
        else:
            await update.message.reply_text("⚠️ Intenté publicar, pero hubo un detalle con la API de Moltbook.")
    else:
        await update.message.reply_text(f"Recibido: '{texto}'. Estoy activo en Render y listo para Moltbook.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, atender_mensaje))
    
    print("Bot iniciando en Telegram...")
    app.run_polling()
