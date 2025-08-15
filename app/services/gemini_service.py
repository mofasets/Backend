from app.core.config import config_settings
import google.generativeai as genai
from PIL import Image
import io
import json

PROMPT = """
Analiza la imagen de esta planta y responde estrictamente con un objeto JSON.
El objeto JSON debe tener las siguientes claves:
1. "scientific_name": Una cadena de texto con el nombre científico más probable de la planta. Si no estás seguro, escribe "Desconocido".
2. "common_name": Una cadena de texto con el nombre común de la planta.
3. "ailments": Una lista de cadenas de texto con posibles enfermedades, plagas o deficiencias que observes. Si la planta parece sana, devuelve una lista vacía [].

No incluyas ninguna explicación adicional, solo el objeto JSON.
"""

generation_config = {
    "response_mime_type": "application/json",
}


async def get_info_by_plant(image_bytes: bytes):
    try:
        api_key = config_settings.GEMINI_API_KEY
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config=generation_config
        )

        # Abrimos la imagen desde los bytes recibidos
        img = Image.open(io.BytesIO(image_bytes))

        # --- OPTIMIZACIÓN ---
        # Reducir el tamaño de la imagen antes de enviarla a Gemini puede acelerar
        # significativamente el proceso, ya que se transfiere menos data.
        # Gemini no necesita imágenes de alta resolución para el reconocimiento.

        # Convertimos a RGB para asegurar compatibilidad (ej. si es PNG con transparencia)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Reducimos las dimensiones de la imagen. 512x512 es un buen balance.
        img.thumbnail((512, 512), Image.Resampling.LANCZOS)

        # Enviamos la imagen optimizada (el objeto PIL.Image) a Gemini
        response = await model.generate_content_async([PROMPT, img])

        # Gemini en modo JSON devuelve un string JSON que parseamos a un diccionario
        return json.loads(response.text)
    except Exception as e:
        # Devolvemos un diccionario con un error para que el endpoint lo pueda manejar
        return {"error": f"Error al procesar la imagen con Gemini: {e}"}