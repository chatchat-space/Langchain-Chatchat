from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field

from chatchat.server.constant.response_code import ResponseCode


def default_data():
    return ""


class BaseResponse(BaseModel):
    code: int = Field(200, description="API status code")
    msg: str = Field("success", description="API status message")
    data: Optional[Union[Any, None]] = Field(default_factory=default_data, description="API data")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": None
            }
        }

    @classmethod
    def success(cls, data: Optional[Any] = "", message: str = "success"):
        return BaseResponse(code=ResponseCode.SUCCESS, msg=message, data=data)

    @classmethod
    def error(cls, data: Optional[Any] = "", message: str = "error", code=ResponseCode.INTERNAL_SERVER_ERROR):
        return BaseResponse(code=code, msg=message, data=data)
