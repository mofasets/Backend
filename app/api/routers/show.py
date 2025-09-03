from fastapi import UploadFile, File, APIRouter, HTTPException, Depends
from app.db.repository_plant import PlantRepository
from app.services.gemini_service import get_info_by_plant
from app.db.repository_plant import PlantRepository
from app.db.repository_interaction import InteractionRepository
from app.schemas.auth import decode_token

show_router = APIRouter(prefix='/show')
TAGS = ['Show']

@show_router.get('/{item_id}', tags=TAGS)
async def show_item(item_id: str, plant_repo: PlantRepository = Depends(PlantRepository),  interaction_repo: InteractionRepository = Depends(InteractionRepository),  my_user = Depends(decode_token)):
    plant = await plant_repo.get_plant_by_id(item_id)

    if plant and my_user:
        existing_interaction = await interaction_repo.find_view_interaction_today(
            user_id=my_user.id,
            plant_id=plant.id
        )
        
        if not existing_interaction:
            content = {
                'user_id': my_user.id,
                'plant_id': plant.id,
                'interaction_type': 'view'
            }
            await interaction_repo.add_interaction(content)        
    return plant
