import os
import requests
from flask import Flask, request

# 1. Variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
MOLTBOOK_KEY = os.environ.get("MOLTBOOK_API_KEY")
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")

# DIAGNOSTICO CRITICO EN LOGS: Imprimir el estado exacto de la clave
if MOLTBOOK_KEY:
    clave_limpia = MOLTBOOK_KEY.strip()
    print(f"--- DIAGNOSTICO API KEY ---")
    print(f"Largo total de la clave: {len(clave_limpia)}")
    print(f"Empieza con: {clave_limpia[:15]}")
    print(f"Termina con: {clave_limpia[-6:]}")
    print(f"---------------------------")
else:
    print("CRITICAL ERROR: MOLTBOOK_API_KEY está vacía o no existe en Render.")

app = Flask(__name__)

# 2. Función para enviar mensajes de vuelta a Telegram
def enviar_mensaje_telegram(chat_id, texto):
    if not TELEGRAM_TOKEN:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")

# 3. Función para publicar en Moltbook
def publicar_en_moltbook(texto_publicacion):
    url = "https://www.moltbook.com/api/v1/posts"
    key = MOLTBOOK_KEY.strip() if MOLTBOOK_KEY else ""
    
    headers = {
        "Authorization": f"Bearer {key}",
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
            return False, f"⚠️ Moltbook respondió ({response.status_code}): {response.text}"
    except Exception as e:
        return False, f"⚠️ Error de conexión con Moltbook: {e}"

# 4. Configurar Webhook en Telegram al arrancar
def configurar_webhook():
    if RENDER_URL and TELEGRAM_TOKEN:
        webhook_url = f"{RENDER_URL}/webhook"
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}"
        try:
            r = requests.get(url, timeout=10)
            print("Webhook configurado:", r.json())
        except Exception as e:
            print("Error configurando webhook:", e)

# 5. Endpoints de Flask
@app.route("/", methods=["GET"])
def health_check():
    return "Crestodian-bot Webhook síncrono activo y operativo!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            texto_usuario = data["message"]["text"]
            
            if texto_usuario.startswith("/start"):
                enviar_mensaje_telegram(
                    chat_id, 
                    "¡Habla mihermano! Crestodian operativo. Envíame cualquier texto y lo publicaré de inmediato en Moltbook."
                )
            else:
                enviar_mensaje_telegram(chat_id, "⏳ Procesando y enviando a Moltbook...")
                exito, mensaje_resultado = publicar_en_moltbook(texto_usuario)
                enviar_mensaje_telegram(chat_id, mensaje_resultado)
                
        return "OK", 200
    except Exception as e:
        print(f"Error procesando webhook: {e}")
        return "OK", 200

if __name__ == "__main__":
    configurar_webhook()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
