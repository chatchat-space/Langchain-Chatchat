from app.services.exceptions.base_exception import BaseAppException


class FileNotExistsException(BaseAppException):
    def __init__(self):
        super().__init__(code=404, message='文件未找到')
