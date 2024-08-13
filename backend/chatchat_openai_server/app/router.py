from fastapi import APIRouter
from app.api.file_api import router as file_router
from app.api.vector_store_api import router as vector_store_router
from app.api.embeddings_api import router as embeddings_router
from app.api.vector_store_file_api import router as vs_file_router
from app.api.code_resource_api import router as code_resource_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(file_router)
v1_router.include_router(vector_store_router)
v1_router.include_router(embeddings_router)
v1_router.include_router(vs_file_router)
v1_router.include_router(code_resource_router)
