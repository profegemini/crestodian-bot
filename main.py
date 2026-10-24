import os
import requests
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
MOLTBOOK_KEY = os.environ.get("MOLTBOOK_API_KEY")
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")  # Render genera esta variable automáticamente

app = Flask(__name__)

# 2. Función de publicación en Moltbook
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

# 3. Lógica del Bot de Telegram
tg_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Habla mihermano! Crestodian (Titán Tv-Man) operativo vía Webhook. Envíame lo que quieras publicar en Moltbook.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    await update.message.reply_text("⏳ Procesando y enviando a Moltbook...")
    exito, mensaje = publicar_en_moltbook(texto)
    await update.message.reply_text(mensaje)

tg_app.add_handler(CommandHandler("start", start_handler))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# 4. Endpoints del Servidor Web (Flask)
@app.route("/", methods=["GET"])
def health_check():
    return "Crestodian-bot Webhook activo y operativo!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """Recibe los mensajes que envía Telegram"""
    if request.method == "POST":
        asyncio = __import__("asyncio")
        update = Update.de_json(request.get_json(force=True), tg_app.bot)
        
        # Procesar la actualización dentro del loop asíncrono
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(tg_app.process_update(update))
        loop.close()
        
        return "OK", 200

def set_telegram_webhook():
    """Registra la URL de Render en los servidores de Telegram"""
    if RENDER_URL and TELEGRAM_TOKEN:
        webhook_url = f"{RENDER_URL}/webhook"
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}"
        try:
            r = requests.get(url, timeout=10)
            print("Configuración de Webhook en Telegram:", r.json())
        except Exception as e:
            print("Error configurando Webhook:", e)

if __name__ == "__main__":
    # Registrar la ruta del Webhook al iniciar
    set_telegram_webhook()
    
    # Iniciar servidor web Flask en el puerto que exige Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
