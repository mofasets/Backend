from fastapi import UploadFile, File, APIRouter, HTTPException, Depends
from app.db.repository_plant import PlantRepository
from beanie import Document
from app.services.gemini_service import get_info_by_plant
from app.db.repository_plant import PlantRepository
from app.schemas.auth import decode_token


explore_router = APIRouter(prefix='/explore')
TAGS = ['Explore']

medicinal_plants = []

@explore_router.post('/recognize_img', tags=TAGS)
async def explore_recognize_img(img: UploadFile = File(...), plant_repo: PlantRepository = Depends(PlantRepository),  my_user = Depends(decode_token)):
    img_bytes_content = await img.read()
    plant_info: dict[str, str] = await get_info_by_plant(img_bytes_content)
    suggested_plants = await plant_repo.get_plants_by_img_result(plant_info.get('scientific_name'), plant_info.get('ailments'))
    response = {
        "img_result": plant_info,
        "suggested_plants": suggested_plants
    }
    return response

@explore_router.get('/{item_id}', tags=TAGS)
async def explore_show(item_id: str, plant_repo: PlantRepository = Depends(PlantRepository),  my_user = Depends(decode_token)):
    plant = await plant_repo.get_plant_by_id(item_id)
    return plant
