from typing import List

from sqlalchemy.orm import Session

from app.db.models.model_record_db_model import ModelRecordDbModel
from app.depends.depend_database import with_session
from app._types.model_object import ModelDeletedObject, ModelObject


class ModelRecordDao:
    @staticmethod
    @with_session
    def create_model(db: Session
                     , org_id: str
                     , model_id: str
                     , owned_by: str
                     , metadata_: dict):
        new_model = ModelRecordDbModel(
            org_id=org_id,
            model_id=model_id,
            owned_by=owned_by,
            metadata_=metadata_
        )
        db.add(new_model)
        db.commit()
        db.refresh(new_model)
        return new_model.to_object()

    @staticmethod
    @with_session
    def list_models(db: Session) -> List[ModelObject]:
        models = db.query(ModelRecordDbModel).all()
        return [model.to_object() for model in models]

    @staticmethod
    @with_session
    def retrieve_model(db: Session, model_id: str) -> ModelObject:
        model = db.query(ModelRecordDbModel).filter(ModelRecordDbModel.model_id == model_id).first()
        if not model:
            return None
        return model.to_object()

    @staticmethod
    @with_session
    def delete_model(db: Session, model_id: str) -> ModelDeletedObject:
        model = db.query(ModelRecordDbModel).filter(ModelRecordDbModel.model_id == model_id).first()
        if not model:
            return None
        db.delete(model)
        db.commit()
        return ModelDeletedObject(id=model_id)
