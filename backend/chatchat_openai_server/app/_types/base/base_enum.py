import enum


class BaseEnum(enum.Enum):

    def __init__(self, code, desc):
        self.code = code
        self.desc = desc
