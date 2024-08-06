from typing import List

from app.db.dao.model_record_dao import ModelRecordDao
from app.types.model_object import ModelDeletedObject, ModelObject


class ModelsService:
    @staticmethod
    def create_model(org_id: str
                     , model_id: str
                     , owned_by: str
                     , metadata_: dict):
        return ModelRecordDao.create_model(
            org_id=org_id,
            model_id=model_id,
            owned_by=owned_by,
            metadata_=metadata_
        )

    @staticmethod
    def list_models() -> List[ModelObject]:
        return ModelRecordDao.list_models()

    @staticmethod
    def retrieve_model(model_id: str) -> ModelObject:
        return ModelRecordDao.retrieve_model(model_id)

    @staticmethod
    def delete_model(model_id: str) -> ModelDeletedObject:
        return ModelRecordDao.delete_model(model_id)
