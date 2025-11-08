from app.core.config import config_settings
import google.generativeai as genai
from PIL import Image
import io
import json

PROMPT = """
Actúa como un etnobotánico experto y un divulgador científico.
Tu tarea es identificar la planta en la imagen y detallar sus usos medicinales en un tono **cercano, claro y fácil de entender** para un público no experto. Evita la jerga científica excesiva en las descripciones.

Responde estrictamente con un único objeto JSON, sin añadir explicaciones, texto introductorio ni formato markdown.

**Regla Crítica: Si la imagen proporcionada NO contiene una planta (por ejemplo, es un animal, un objeto inanimado, una persona, etc.), debes devolver el JSON con todos los campos como cadenas de texto vacías ("") o listas vacías ([]), según corresponda.**

El objeto JSON debe seguir esta estructura exacta:
{
  "scientific_name": "string",
  "common_names": ["string"],
  "habitat_description": "string",
  "general_ailments": "string",
  "specific_diseases": ["string"],
  "usage_instructions": "string",
  "taxonomy": "string",
  "active_ingredient": "string",
  "references": ["string"]
}

Instrucciones detalladas para el contenido de cada clave:

1.  **"scientific_name"**: Proporciona el nombre científico más probable. **Es crucial que si es imposible identificar la planta o si la imagen no contiene una planta, devuelvas una cadena de texto vacía ""**.
2.  **"common_names"**: Devuelve una lista de nombres comunes, priorizando los usados en Latinoamérica y Venezuela. Si no se encuentran o aplica la regla crítica, devuelve [].
3.  **"habitat_description"**: Redacta una descripción breve (2-3 líneas) del hábitat natural de la especie, **en un tono fácil de entender** (ej. "Le gusta crecer en..."). Si no dispones de esta información o aplica la regla crítica, devuelve "".
4.  **"general_ailments"**: En una sola cadena, resume las categorías generales de dolencias que trata (ej: "Ayuda con la inflamación, el dolor y problemas respiratorios"). Si no se conocen usos medicinales o aplica la regla crítica, devuelve "".
5.  **"specific_diseases"**: Devuelve una lista de enfermedades específicas (ej: ["Artritis", "Gripe", "Cistitis"]). Si no se conocen o aplica la regla crítica, devuelve [].
6.  **"usage_instructions"**: Redacta el modo de empleo **en un tono cercano y educativo**. Debe tener un **mínimo de dos párrafos** y describir **al menos dos métodos de preparación distintos** (ej: infusión, cataplasma). **Incluye una advertencia de seguridad clara y directa** si la planta lo requiere. Si no se conocen modos de empleo o aplica la regla crítica, devuelve "".
7.  **"taxonomy"**: Redacta una descripción breve (2-3 líneas) de su clasificación, **explicada de forma sencilla** (ej. "Pertenece a la familia de las Fabaceae, lo que significa que es 'pariente' de los frijoles..."). Si no aplica, devuelve "".
8.  **"active_ingredient"**: Redacta una descripción breve (2-3 líneas) de sus principios activos, **evitando jerga química y explicando su función** (ej. "Contiene taninos, que son compuestos que ayudan a secar y desinflamar la piel..."). Si no aplica, devuelve "".
9.  **"references"**: Proporciona una lista de 2 a 3 referencias bibliográficas (formato APA o similar) que validen la información. Si no hay referencias directas o aplica la regla crítica, devuelve [].
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