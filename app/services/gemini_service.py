from app.core.config import config_settings
import google.generativeai as genai
from PIL import Image
import io
import json

PROMPT = """
Actúa como un etnobotánico experto y un divulgador científico.
Tu tarea es identificar la planta en la imagen y clasificarla.

Responde estrictamente con un único objeto JSON, sin añadir explicaciones, texto introductorio ni formato markdown.

**Regla Crítica: Si la imagen NO contiene una planta (ej. un animal, un objeto), debes devolver el JSON con todos los campos como cadenas de texto vacías ("") o listas vacías ([]).**

El objeto JSON debe seguir esta estructura exacta:
{
  "scientific_name": "string",
  "common_names": ["string"],
  "safety_level": "string",
  "habitat_description": "string",
  "general_ailments": "string",
  "specific_diseases": ["string"],
  "usage_instructions": "string",
  "taxonomy": "string",
  "active_ingredient": "string",
  "references": ["string"]
}

---
**INSTRUCCIONES DETALLADAS POR CAMPO:**

**CAMPOS DE IDENTIFICACIÓN BÁSICA (Llenar siempre si se identifica la planta):**

1.  **"scientific_name"**: El nombre científico. Si no puedes identificarla, devuelve "".
2.  **"common_names"**: Lista de nombres comunes (priorizando Latinoamérica).
3.  **"safety_level"**: Clasifica la planta en UNA de estas tres categorías exactas:
    * **"Medicinal"**: Si tiene usos etnobotánicos conocidos y seguros.
    * **"Neutral"**: Si es ornamental, comestible común o silvestre sin usos medicinales (ej. una rosa, césped).
    * **"Toxic"**: Si la planta es conocida por ser peligrosa o venenosa (ej. Dieffenbachia).
4.  **"habitat_description"**: Descripción breve y sencilla de su hábitat.
5.  **"taxonomy"**: Descripción taxonómica sencilla (ej. "Pariente de los frijoles...").
6.  **"references"**: 2-3 referencias bibliográficas (formato APA o similar).

**CAMPOS DE USO MEDICINAL (Llenar solo si "safety_level" es "Medicinal"):**
*(Si "safety_level" es "Neutral" o "Toxic", estos campos deben ir vacíos: "" o [].)*

7.  **"general_ailments"**: (Solo si es "Medicinal") Resumen de las dolencias que trata. Si no, devuelve "".
8.  **"specific_diseases"**: (Solo si es "Medicinal") Lista de enfermedades específicas. Si no, devuelve [].
9.  **"usage_instructions"**: (Solo si es "Medicinal") Redacta el modo de empleo en tono cercano (2 párrafos, 2 métodos) e incluye advertencias si las tiene. Si no, devuelve "".
10. **"active_ingredient"**: (Solo si es "Medicinal") Descripción sencilla de su principio activo (ej. "Contiene taninos, que ayudan a desinflamar..."). Si no, devuelve "".
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