import aiofiles
from fastapi import UploadFile, APIRouter, File, Depends, Form, HTTPException, status
from app.db.repository_plant import PlantRepository
from app.schemas.auth import decode_token
from app.schemas.plant import PlantRead, PlantForm, Plant
from pathlib import Path
from typing import Optional
import os

TAGS = ['Plants']
plant_router = APIRouter(prefix='/plant')
IMAGE_DIR = Path("app/static/images/plants")

@plant_router.post('/create', tags=TAGS, response_model=Plant)
async def create_plant(data: str = Form(...), img: UploadFile = File(...), plant_repo: PlantRepository = Depends(PlantRepository), my_user = Depends(decode_token)):
    

    
    try:
        plant_form_data = PlantForm.model_validate_json(data)

        plant_data = plant_form_data.model_dump()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de validación JSON: {e}"
        )

    existing_plant = await plant_repo.get_plant_by_scientific_name(plant_data.get('scientific_name'))
    if existing_plant:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Una planta con este nombre científico ya existe."
        )
    
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    sanitized_name = "".join(c if c.isalnum() else "_" for c in plant_data.get('scientific_name').lower())
    new_filename = f"{sanitized_name}.jpg"
    file_path = IMAGE_DIR / new_filename

    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await img.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error al guardar la imagen: {e}"
        )
        
    plant_data["common_names"] = [name.strip() for name in plant_form_data.common_names.split(',')]
    plant_data["specific_diseases"] = [d.strip() for d in plant_form_data.specific_diseases.split(',')]
    plant_data["references"] = [r.strip() for r in plant_form_data.references.split(';')] if plant_form_data.references else []
    plant_data["image_filename"] = new_filename
        
    plant_id = await plant_repo.add_plant(plant_data)
    return plant_id

@plant_router.put('/edit', tags=TAGS, response_model=PlantRead)
async def update_plant(data: str = Form(...), img: Optional[UploadFile] = File(None), plant_repo: PlantRepository = Depends(PlantRepository), my_user = Depends(decode_token)):
    
    try:
        plant_form_data = PlantForm.model_validate_json(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de validación JSON: {e}"
        )

    update_data = plant_form_data.model_dump()

    existing_plant = await plant_repo.get_plant_by_scientific_name(plant_form_data.scientific_name)
    if not existing_plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró una planta con ese nombre científico para editar."
        )
    
    if img:
        print("Nueva imagen detectada. Reemplazando...")
        IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        
        sanitized_name = "".join(c if c.isalnum() else "_" for c in plant_form_data.scientific_name.lower())
        new_filename = f"{sanitized_name}.jpg"
        file_path = IMAGE_DIR / new_filename

        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = await img.read()
                await f.write(content)
            
            update_data["image_filename"] = new_filename
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error al guardar la nueva imagen: {e}"
            )
    else:
        if "image_filename" in update_data:
            del update_data["image_filename"]

    update_data["common_names"] = [name.strip() for name in plant_form_data.common_names.split(',')]
    update_data["specific_diseases"] = [d.strip() for d in plant_form_data.specific_diseases.split(',')]
    update_data["references"] = [r.strip() for r in plant_form_data.references.split(';')] if plant_form_data.references else []

    updated_plant = await plant_repo.update_plant(existing_plant.id, update_data)
    if not updated_plant:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="La planta no pudo ser actualizada en la base de datos."
        )

    return updated_plant

@plant_router.delete('/delete/{plant_id}', tags=TAGS, response_model=PlantRead)
async def delete_plant(plant_id: str, plant_repo: PlantRepository = Depends(PlantRepository), my_user: dict = Depends(decode_token)):
    
    try:
        deleted_plant = await plant_repo.delete_plant(plant_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El ID de planta proporcionado no es válido: {e}"
        )

    if not deleted_plant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planta no encontrada."
        )

    if deleted_plant.image_filename:
        file_path = IMAGE_DIR / deleted_plant.image_filename
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Archivo de imagen eliminado: {file_path}")
            except Exception as e:
                print(f"Error al eliminar el archivo de imagen: {e}")
        else:
            print(f"Advertencia: No se encontró el archivo de imagen: {file_path}")

    return deleted_plant