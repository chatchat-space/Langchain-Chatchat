from pydantic import BaseModel


class ModelObject(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str
    metadata: dict


class ListModelObject(BaseModel):
    object: str = "list"
    data: list[ModelObject] = []


class ModelDeletedObject(BaseModel):
    id: str
    object: str = 'model'
    deleted: bool = True
