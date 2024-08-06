class BaseAppException(Exception):
    def __init__(self, code=500, message: str = ''):
        self.message = message
        self.code = code
