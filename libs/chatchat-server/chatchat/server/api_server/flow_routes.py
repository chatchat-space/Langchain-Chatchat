from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Body, Request

from chatchat.server.utils import BaseResponse
from chatchat.utils import build_logger
from chatchat.server.api_server.api_schemas import FlowParams
import importlib
from chatchat.server.langgraph import node_factory
importlib.reload(node_factory)
from chatchat.server.langgraph.node_factory.build_flow import build_flow
from langgraph.graph.graph import CompiledGraph
logger = build_logger()

flow_router = APIRouter(prefix="/flows", tags=["flows"])




#测试API接口，后续会废弃，整合到chat接口
@flow_router.post("/build_flow_and_run", response_model=BaseResponse)
async def build_flow_and_run(
    flow_params: FlowParams
):
    try:
        print(flow_params.model_dump_json())
        flow_params_dict=flow_params.model_dump()
        flow:CompiledGraph=build_flow(flow_params_dict)
        state=flow.invoke({"state":{"question":flow_params.question}})
        return {"data": state}
    except Exception:
        msg = f"failed to build flow"
        logger.error(msg, exc_info=True)
        return {"code": 500, "msg": msg}
