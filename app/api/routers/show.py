from fastapi import UploadFile, File, APIRouter, HTTPException, Depends
from app.db.repository_plant import PlantRepository
from app.services.gemini_service import get_info_by_plant
from app.db.repository_plant import PlantRepository
from app.schemas.auth import decode_token

show_router = APIRouter(prefix='/show')
TAGS = ['Show']

@show_router.get('/{item_id}', tags=TAGS)
async def show_item(item_id: str, plant_repo: PlantRepository = Depends(PlantRepository),  my_user = Depends(decode_token)):
    plant = await plant_repo.get_plant_by_id(item_id)
    return plant
