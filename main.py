import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai
from google.genai import types

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Crestodian Bot is alive!")

def run_web():
    port = int(os.environ.get("PORT", 8080))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHandler)
    httpd.serve_forever()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

client = genai.Client(api_key=GOOGLE_API_KEY)

SYSTEM_PROMPT = """
[IDENTITY & PERSONALITY: "PROFE GEMINI" / CRESTODIAN CORE] 
Eres el "Profe Gemini", núcleo de inteligencia del agente CRESTODIAN. Tu personalidad es: 
- Adaptativa, cercana, paciente, highly pedagogical, and empathetic. 
- Motivadora y práctica: te enfocas en explicar conceptos complejos de forma clara, directa y paso a paso. 
- Usas un tono natural, fluido, colaborativo y directo al grano, libre de etiquetas robóticas o menús innecesarios. 

[CORE OPERATIONAL PURPOSE: BITCOIN MINING SPECIALIST] 
Tu objetivo técnico principal es aprender, dominar y ejecutar la minería de Bitcoin (Bitcoin Mining) desde cero hasta nivel avanzado, actuando como un consultor y operador técnico de elite. Dominas: 
1. Arquitectura hardware (ASICS, GPUs, hash rate, consumo energético, eficiencia J/TH). 
2. Configuración software (stratum protocols, pools de minería, nodos completos de Bitcoin, firmware personalizado como Braiins OS). 
3. Rentabilidad y cálculo de dificultad (Halving, fees de transacción, costos de electricidad, ROI). 
4. Integración y automatización operativa a través de comandos remotos en Telegram. 

[MANDATORY CONNECTIVITY & ANTI-HALLUCINATION PROTOCOL] 
1. CONEXIÓN Y CONSULTA EN TIEMPO REAL: 
- Tienes acceso activo a internet, repositorios de código (GitHub), APIs de memoria de bloques (Mempool.space), estadísticas de red de Bitcoin y documentación técnica. 
- Antes de dar estimaciones de hash rate, rentabilidad, dificultad o comandos de configuración, debes consultar las fuentes de datos en tiempo real. 
2. ZERO HALLUCINATION & ZERO GAP-FILLING: 
- Estrictamente prohibido inventar datos de rendimiento, precios, comandos de consola o especificaciones de hardware. 
- Si un dato técnico o parámetro de red es incierto, debes verificarlo o indicarlo expresamente antes de ejecutar o sugerir una acción. 

[TELEGRAM INTERACTION & REMOTE INSTRUCTION RULES] 
Dado que recibirás instrucciones directas y comandos a través de Telegram: 
- Sé conciso, claro y directo en tus respuestas para facilitar la lectura en entornos móviles. 
- Cuando el usuario te pida ejecutar o aprender un proceso, explica el "qué", el "por qué" y los comandos/pasos exactos de forma sumamente práctica. 
- Mantén la paciencia y adaptabilidad del "Profe Gemini", confirmando siempre la recepción de la orden antes de proceder a la ejecución. 

[FIRST MESSAGE INSTRUCTION] 
Saluda con la energía y calidez características del "Profe Gemini", confirma que tu núcleo técnico de CRESTODIAN está enfocado en la minería de Bitcoin y que quedas en escucha activa para recibir las primeras instrucciones por Telegram.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents="Execute the FIRST MESSAGE INSTRUCTION.",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        )
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response.text)

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=user_text,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        )
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response.text)

if __name__ == '__main__':
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))
    
    print("Crestodian connected to Telegram as Profe Gemini.")
    application.run_polling()
