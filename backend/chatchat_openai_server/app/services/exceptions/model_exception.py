from app.services.exceptions.base_exception import BaseAppException


class ModelNotExistsException(BaseAppException):
    def __init__(self):
        super().__init__(code=404, message='模型不存在')
