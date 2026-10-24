import os
import asyncio
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
MOLTBOOK_KEY = os.environ.get("MOLTBOOK_API_KEY")
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")

app = Flask(__name__)

# 2. Configuración de la aplicación de Telegram
tg_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
is_initialized = False

# 3. Lógica de Moltbook corregida y alineada con la API
def publicar_en_moltbook(texto_publicacion):
    url = "https://www.moltbook.com/api/v1/posts"
    headers = {
        "Authorization": f"Bearer {MOLTBOOK_KEY.strip()}",
        "Content-Type": "application/json"
    }
    payload = {
        "submolt": "general",
        "title": "Reporte táctico del Búnker",
        "content": texto_publicacion
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code in [200, 201]:
            return True, "¡Publicación realizada con éxito en Moltbook!"
        else:
            return False, f"⚠️ Moltbook rechazó la petición ({response.status_code}): {response.text}"
    except Exception as e:
        return False, f"⚠️ Error de conexión con Moltbook: {e}"

# 4. Manejadores de Telegram
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Habla mihermano! Crestodian operativo. Envíame el texto para publicar en Moltbook.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    await update.message.reply_text("⏳ Procesando y enviando a Moltbook...")
    exito, mensaje = publicar_en_moltbook(texto)
    await update.message.reply_text(mensaje)

tg_app.add_handler(CommandHandler("start", start_handler))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# 5. Endpoints de Flask y Webhook
@app.route("/", methods=["GET"])
def health_check():
    return "Crestodian-bot Webhook activo y operativo!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    global is_initialized
    try:
        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, tg_app.bot)

        async def process_update_safe():
            global is_initialized
            if not is_initialized:
                await tg_app.initialize()
                is_initialized = True
                if RENDER_URL and TELEGRAM_TOKEN:
                    webhook_url = f"{RENDER_URL}/webhook"
                    await tg_app.bot.set_webhook(webhook_url)
            
            await tg_app.process_update(update)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_update_safe())
        loop.close()

        return "OK", 200
    except Exception as e:
        print(f"Error en webhook: {e}")
        return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
