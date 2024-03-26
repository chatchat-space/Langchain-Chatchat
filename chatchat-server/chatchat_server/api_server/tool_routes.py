from __future__ import annotations

from typing import List

from fastapi import APIRouter, Request, Body

from configs import logger
from chatchat_server.utils import BaseResponse


tool_router = APIRouter(prefix="/tools", tags=["Toolkits"])


@tool_router.get("/", response_model=BaseResponse)
async def list_tools():
    import importlib
    from chatchat_server.agent.tools_factory import tools_registry
    importlib.reload(tools_registry)

    data = {t.name: {"name": t.name, "description": t.description, "args": t.args} for t in tools_registry.all_tools}
    return {"data": data}


@tool_router.post("/call", response_model=BaseResponse)
async def call_tool(
    name: str = Body(examples=["calculate"]),
    kwargs: dict = Body({}, examples=[{"a":1,"b":2,"operator":"+"}]),
):
    import importlib
    from chatchat_server.agent.tools_factory import tools_registry
    importlib.reload(tools_registry)

    tool_names = {t.name: t for t in tools_registry.all_tools}
    if tool := tool_names.get(name):
        try:
            result = await tool.ainvoke(kwargs)
            return {"data": result}
        except Exception:
            msg = f"failed to call tool '{name}'"
            logger.error(msg, exc_info=True)
            return {"code": 500, "msg": msg}
    else:
        return {"code": 500, "msg": f"no tool named '{name}'"}
