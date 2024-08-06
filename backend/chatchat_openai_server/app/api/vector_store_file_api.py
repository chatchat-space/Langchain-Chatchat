from fastapi import APIRouter
from pydantic import BaseModel

from app.services.vector_store_file_service import VectorStoreFileService
from app.types.vector_store_file_object import VectorStoreFileObject, ListVectorStoreFileObject

router = APIRouter(prefix="/vector_stores", tags=["vector_stores file"])


class CreateVectorStoreFileRequest(BaseModel):
    file_id: str


@router.post("/{vector_store_id}/files", response_model=VectorStoreFileObject)
def create_vector_store_file(vector_store_id: str
                             , request: CreateVectorStoreFileRequest
                             ):
    return VectorStoreFileService.create_vector_store_file(vector_store_id, request.file_id)


@router.get("/{vector_store_id}/files", response_model=ListVectorStoreFileObject)
def list_vector_store_files(vector_store_id: str):
    return VectorStoreFileService.list_vector_store_files(vector_store_id)


@router.get("/{vector_store_id}/files/{file_id}", response_model=VectorStoreFileObject)
def retrieve_vector_store_file(vector_store_id: str, file_id: str):
    return VectorStoreFileService.retrieve_vector_store_file(vector_store_id, file_id)


@router.delete("/{vector_store_id}/files/{file_id}")
def delete_vector_store_file(vector_store_id: str, file_id: str):
    return VectorStoreFileService.delete_vector_store_file(vector_store_id, file_id)
