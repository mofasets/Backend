from app.core.config import config_settings
import google.generativeai as genai
from PIL import Image
import io
import json

PROMPT = """
Actúa como un etnobotánico experto y un especialista en herbolaria. Tu tarea es identificar la planta en la imagen y detallar sus usos medicinales. Responde estrictamente con un único objeto JSON, sin añadir explicaciones, texto introductorio ni formato markdown.

**Regla Crítica: Si la imagen proporcionada NO contiene una planta (por ejemplo, es un animal, un objeto inanimado, una persona, un paisaje sin una planta dominante, etc.), debes devolver el JSON con todos los campos como cadenas de texto vacías ("") o listas vacías ([]), según corresponda.**

El objeto JSON debe seguir esta estructura exacta:
{
  "scientific_name": "string",
  "common_names": ["string"],
  "habitat_description": "string",
  "general_ailments": "string",
  "specific_diseases": ["string"],
  "usage_instructions": "string"
}

Instrucciones detalladas para el contenido de cada clave:

1.  **"scientific_name"**: Proporciona el nombre científico más probable de la planta. **Es crucial que si es imposible identificar la planta o si la imagen no contiene una planta, devuelvas una cadena de texto vacía ""**.
2.  **"common_names"**: Devuelve una lista de cadenas de texto con los nombres comunes más conocidos, priorizando los usados en Latinoamérica y España. Si no se encuentran o aplica la regla crítica, devuelve una lista vacía [].
3.  **"habitat_description"**: Redacta una descripción breve del hábitat natural de la especie. Si no dispones de esta información o aplica la regla crítica, devuelve una cadena de texto vacía "".
4.  **"general_ailments"**: En una sola cadena, resume las categorías generales de dolencias que la planta puede tratar (ej: "Inflamación, dolor, infecciones, problemas respiratorios"). Si no se conocen usos medicinales o aplica la regla crítica, devuelve una cadena de texto vacía "".
5.  **"specific_diseases"**: Devuelve una lista de enfermedades o condiciones específicas para las cuales se utiliza la planta (ej: ["Artritis", "Gripe", "Cistitis"]). Si no se conocen aplicaciones específicas o aplica la regla crítica, devuelve una lista vacía [].
6.  **"usage_instructions"**: Redacta el modo de empleo de la planta, detallando cómo prepararla y aplicarla para los malestares mencionados. El texto debe tener un **mínimo de dos párrafos** y describir **al menos dos métodos de preparación o aplicación distintos** (ej: infusión, decocción, cataplasma, jarabe, baño, etc.). Si la planta es tóxica o requiere un uso cuidadoso, inclúyelo como una advertencia. Si no se conocen modos de empleo o aplica la regla crítica, devuelve una cadena de texto vacía "".
"""
generation_config = {
    "response_mime_type": "application/json",
}


async def get_info_by_plant(image_bytes: bytes):
    try:
        api_key = config_settings.GEMINI_API_KEY
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            'gemini-2.5-flash-lite',
            generation_config=generation_config,
        )
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.thumbnail((512, 512), Image.Resampling.LANCZOS)
        response = await model.generate_content_async([PROMPT, img])
        
        raw_text = response.text
        cleaned_text = raw_text.strip().replace("```json", "").replace("```", "").strip()
        
        return json.loads(cleaned_text)
    
    except Exception as e:
        return {"error": f"Error al procesar la imagen con Gemini: {e}"}