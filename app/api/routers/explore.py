from fastapi import UploadFile, File, APIRouter, HTTPException, Depends
from app.db.repository_plant import PlantRepository
from app.services.gemini_service import get_info_by_plant
from app.db.repository_plant import PlantRepository
from app.schemas.auth import decode_token
from app.schemas.plant import RecognitionResponse

explore_router = APIRouter(prefix='/explore')
TAGS = ['Explore']

medicinal_plants = []

@explore_router.post('/recognize_img', tags=TAGS, response_model=RecognitionResponse)
async def explore_recognize_img(img: UploadFile = File(...), plant_repo: PlantRepository = Depends(PlantRepository)):
    img_bytes_content = await img.read()
    plant_info = await get_info_by_plant(img_bytes_content)
    suggested_plants = await plant_repo.get_plants_by_img_result(plant_info.get('scientific_name'), plant_info.get('specific_diseases'))
    response = {
        "img_result": plant_info,
        "suggested_plants": suggested_plants
    }
    return response
