from app.core.config import config_settings
import google.generativeai as genai
from PIL import Image
import io
import json

PROMPT = """
Actúa como un etnobotánico experto y un especialista en herbolaria. Tu tarea es identificar la planta en la imagen y detallar sus usos medicinales. Responde estrictamente con un único objeto JSON, sin añadir explicaciones, texto introductorio ni formato markdown.

El objeto JSON debe seguir esta estructura exacta:
{
  "scientific_name": "string",
  "common_names": ["string"],
  "habitat_description": "string",
  "general_ailments": "string",
  "specific_diseases": ["string"]
}

Instrucciones detalladas para el contenido de cada clave:

1.  **"scientific_name"**: Proporciona el nombre científico más probable de la planta. Si es imposible identificarla, devuelve una cadena de texto vacía "".
2.  **"common_names"**: Devuelve una lista de cadenas de texto con los nombres comunes más conocidos de la planta, priorizando los usados en Latinoamérica y España. Si no se encuentran, devuelve una lista vacía [].
3.  **"habitat_description"**: Redacta una descripción breve del hábitat natural y las condiciones de crecimiento de esta especie. Si no dispones de esta información, devuelve una cadena de texto vacía "".
4.  **"general_ailments"**: En una sola cadena de texto, resume las **categorías generales de dolencias humanas** que esta planta puede tratar. Por ejemplo: "Inflamación, dolor, infecciones, problemas respiratorios, reumatismo". Si no se conocen usos medicinales, devuelve una cadena de texto vacía "".
5.  **"specific_diseases"**: Devuelve una lista de cadenas de texto con **enfermedades o condiciones humanas específicas** para las cuales se utiliza la planta. Por ejemplo: ["Artritis", "Gripe", "Cistitis", "Dolor de muelas"]. Si no se conocen aplicaciones específicas, devuelve una lista vacía [].
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

        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.thumbnail((512, 512), Image.Resampling.LANCZOS)
        response = await model.generate_content_async([PROMPT, img])

        return json.loads(response.text)
    except Exception as e:
        return {"error": f"Error al procesar la imagen con Gemini: {e}"}