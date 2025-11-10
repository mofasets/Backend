import aiofiles
from pathlib import Path
from fastapi import UploadFile, File, APIRouter, HTTPException, Depends
from app.db.repository_plant import PlantRepository
from app.services.gemini_service import get_info_by_plant
from app.db.repository_plant import PlantRepository
from app.db.repository_interaction import InteractionRepository
from app.db.repository_user import UserRepository
from app.schemas.auth import decode_token
from app.schemas.plant import RecognitionResponse

explore_router = APIRouter(prefix='/explore')
TAGS = ['Explore']

medicinal_plants = []
IMAGE_DIR = Path("app/static/images/plants")

@explore_router.post('/recognize_img', tags=TAGS, response_model=RecognitionResponse)
async def explore_recognize_img(img: UploadFile = File(...), plant_repo: PlantRepository = Depends(PlantRepository), interaction_repo: InteractionRepository = Depends(InteractionRepository), my_user=Depends(decode_token)):
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    img_bytes_content = await img.read()
    plant_info = await get_info_by_plant(img_bytes_content)
    scientific_name = plant_info.get('scientific_name') if isinstance(plant_info, dict) else None
    
    if not scientific_name or not scientific_name.strip():
        raise HTTPException(
            status_code=502,
            detail="No se pudo identificar la planta de manera confiable o la respuesta del servicio de IA fue inválida."
        )

    is_store = await plant_repo.is_plant_in_db(plant_info.get('scientific_name'))
    plant_in_db = await plant_repo.get_plant_by_scientific_name(plant_info.get('scientific_name'))
    
    if not is_store and plant_info.get('scientific_name'):

        scientific_name = plant_info.get('scientific_name')
        sanitized_name = "".join(c if c.isalnum() else "_" for c in scientific_name.lower())
        new_filename = f"{sanitized_name}.jpg"
        file_path = IMAGE_DIR / new_filename
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(img_bytes_content)
            
        plant_info['image_filename'] = new_filename
        plant_in_db = await plant_repo.add_plant(plant_info)

    if plant_in_db and my_user:
        print('Creando Interaccion')
        content = {
            'user_id': my_user.id,
            'plant_id': plant_in_db.id,
            'interaction_type': 'recognize'
        }
        await interaction_repo.add_interaction(content)

    suggested_plants = await plant_repo.get_plants_by_img_result(plant_info.get('scientific_name'), plant_info.get('specific_diseases'))

    response = {
        "img_result": plant_info,
        "suggested_plants": suggested_plants
    }
    return response

