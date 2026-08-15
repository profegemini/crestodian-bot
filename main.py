import os
from google import genai
from google.genai import types

api_key = os.environ.get("CLAVE_API_DE_GOOGLE")
client = genai.Client(api_key=api_key)
model = 'gemini-2.5-flash'

def obtener_respuesta_crestodian(mensaje):
    respuesta = client.models.generate_content(
        model=model,
        contents=mensaje
    )
    return respuesta.text

if __name__ == "__main__":
    print("CRESTODIAN listo para migrar a la nube.")

import time
# Mantener el proceso vivo para Render
while True:
    time.sleep(3600)
