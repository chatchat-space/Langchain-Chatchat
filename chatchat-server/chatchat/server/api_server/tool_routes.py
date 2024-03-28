from __future__ import annotations

from typing import List

from fastapi import APIRouter, Request, Body

from chatchat.configs import logger
from chatchat.server.utils import BaseResponse, get_tool


tool_router = APIRouter(prefix="/tools", tags=["Toolkits"])


@tool_router.get("/", response_model=BaseResponse)
async def list_tools():
    tools = get_tool()
    data = {t.name: {"name": t.name, "description": t.description, "args": t.args} for t in tools}
    return {"data": data}


@tool_router.post("/call", response_model=BaseResponse)
async def call_tool(
    name: str = Body(examples=["calculate"]),
    kwargs: dict = Body({}, examples=[{"a":1,"b":2,"operator":"+"}]),
):
    tools = get_tool()

    if tool := tools.get(name):
        try:
            result = await tool.ainvoke(kwargs)
            return {"data": result}
        except Exception:
            msg = f"failed to call tool '{name}'"
            logger.error(msg, exc_info=True)
            return {"code": 500, "msg": msg}
    else:
        return {"code": 500, "msg": f"no tool named '{name}'"}
