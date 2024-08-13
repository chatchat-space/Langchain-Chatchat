from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services.vector_store_service import VectorStoreService
from app._types.vector_store_object import VectorStoreObject, VectorStoreDeletedObject, ListVectorStoreObject

router = APIRouter(prefix="/vector_stores", tags=["vector_stores"])


class ChunkingStrategy(BaseModel):
    strategy: str


class ExpiresAfter(BaseModel):
    days: int


class VectorStoreCreateRequest(BaseModel):
    file_ids: Optional[List[str]] = None
    name: Optional[str] = None
    expires_after: Optional[ExpiresAfter] = None
    chunking_strategy: Optional[ChunkingStrategy] = None
    metadata: Optional[Dict[str, Any]] = None


class UpdateVectorStoreRequest(BaseModel):
    name: Optional[str] = None


class VectorStoreResponse(BaseModel):
    id: str
    object: str
    created_at: int
    usage_bytes: int
    last_active_at: int
    name: str
    status: str
    file_counts: Dict[str, Any]
    metadata: Dict[str, Any]
    last_used_at: int


@router.post("", response_model=VectorStoreObject)
def create_vector_store(request: VectorStoreCreateRequest):
    return VectorStoreService.create_vector_store(request.name, request.metadata)


@router.get("", response_model=ListVectorStoreObject)
def list_vector_store(
        limit: int = Query(20, gt=0, le=100),
        order: str = Query("desc", regex="^(asc|desc)$"),
        after: Optional[str] = None,
        before: Optional[str] = None,
):
    return VectorStoreService.list_vector_store(limit, order, after, before)


@router.get("/{vector_store_id}", response_model=VectorStoreObject)
def retrieve_vector_store(vector_store_id: str):
    return VectorStoreService.retrieve_vector_store(vector_store_id)


@router.post("/{vector_store_id}", response_model=VectorStoreObject)
def modify_vector_store(vector_store_id: str, update: UpdateVectorStoreRequest):
    return VectorStoreService.modify_vector_store(vector_store_id, update)


@router.delete("/{vector_store_id}", response_model=VectorStoreDeletedObject)
def delete_vector_store(vector_store_id: str):
    return VectorStoreService.delete_vector_store(vector_store_id=vector_store_id)
