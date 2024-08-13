from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.models_service import ModelsService
from app._types.model_object import ModelObject, ModelDeletedObject

router = APIRouter(prefix="/models", tags=["models"])


class CreateModelRequest(BaseModel):
    ...


@router.post("/models", response_model=ModelObject)
def create_model(request: CreateModelRequest) -> ModelObject:
    return ModelsService.create_model(org_id=request.org_id,
                                      model_id=request.model_id,
                                      owned_by=request.owned_by,
                                      metadata_=request.metadata_)


@router.get("/models", response_model=List[ModelObject])
def list_models():
    return ModelsService.list_models()


@router.get("/models/{model_id}", response_model=ModelObject)
def retrieve_model(model_id: str):
    return ModelsService.retrieve_model(model_id)


@router.delete("/models/{model_id}")
def delete_model(model_id: str) -> ModelDeletedObject:
    return ModelsService.delete_model(model_id)
