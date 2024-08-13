from fastapi import APIRouter

from app.db.models import CodeResourceDbModel
from app.services.code_resource_service import CodeResourceService
from app._types.code_resource_object import CodeResourceObject

router = APIRouter(prefix="/code_resource", tags=["code_resource"])


@router.post("")
def create_code_resource(item: CodeResourceObject):
    return CodeResourceService.add(CodeResourceDbModel(**item.dict()))
