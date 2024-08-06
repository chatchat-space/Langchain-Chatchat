from fastapi import APIRouter, UploadFile, File
from fastapi.params import Form

from app.api.exceptions.base import NotFoundException
from app.services.file_service import FileService
from app.types.file_object import FileObject, FilePurpose, ListFileObject, FileDeletedObject

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIRECTORY = "uploads"  # 本地存储目录


@router.post("/upload", response_model=FileObject)
def upload_file(
        file: UploadFile = File(...),
        metadata: str = Form({}),
        purpose: str = Form(FilePurpose.ASSISTANTS.code)
) -> FileObject:
    return FileService.upload_file(file, metadata, purpose)


@router.get("/list", response_model=ListFileObject)
def file_list(purpose: str = FilePurpose.ASSISTANTS.code):
    return FileService.file_list(purpose)


@router.get("/{file_id}", response_model=FileObject)
def retrieve_file(file_id: str):
    file_object = FileService.retrieve_file(file_id)
    if file_object:
        return file_object
    else:
        raise NotFoundException()


@router.delete("/{file_id}", response_model=FileDeletedObject)
def delete_file(file_id: str):
    file_deleted_object = FileService.delete_file(file_id)
    if file_deleted_object:
        return file_deleted_object
    else:
        raise NotFoundException()


@router.get("/{file_id}/content")
def retrieve_file_content(file_id: str):
    return FileService.retrieve_file_content(file_id)
