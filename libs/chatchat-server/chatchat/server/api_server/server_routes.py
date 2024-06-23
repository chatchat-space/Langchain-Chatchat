from typing import Literal

from fastapi import APIRouter, Body

from chatchat.server.utils import get_prompt_template, get_server_configs

server_router = APIRouter(prefix="/server", tags=["Server State"])


# 服务器相关接口
server_router.post(
    "/configs",
    summary="获取服务器原始配置信息",
)(get_server_configs)


@server_router.post("/get_prompt_template", summary="获取服务区配置的 prompt 模板")
def get_server_prompt_template(
    type: Literal["llm_chat", "knowledge_base_chat"] = Body(
        "llm_chat", description="模板类型，可选值：llm_chat，knowledge_base_chat"
    ),
    name: str = Body("default", description="模板名称"),
) -> str:
    return get_prompt_template(type=type, name=name)
