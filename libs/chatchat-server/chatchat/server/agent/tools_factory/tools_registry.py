from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union

from langchain.agents import tool
from langchain_core.tools import BaseTool

from chatchat.server.knowledge_base.kb_doc_api import DocumentWithVSId
from chatchat.server.pydantic_v1 import BaseModel, Extra

__all__ = ["regist_tool", "BaseToolOutput", "format_context"]

from langchain_chatchat.agent_toolkits import BaseToolOutput

_TOOLS_REGISTRY = {}


def regist_tool(
        *args: Any,
        title: str = "",
        description: str = "",
        return_direct: bool = False,
        args_schema: Optional[Type[BaseModel]] = None,
        infer_schema: bool = True,
) -> Union[Callable, BaseTool]:
    """
    wrapper of langchain tool decorator
    add tool to regstiry automatically
    """

    def _parse_tool(t: BaseTool):
        nonlocal description, title

        _TOOLS_REGISTRY[t.name] = t

        # change default description
        if not description:
            if t.func is not None:
                description = t.func.__doc__
            elif t.coroutine is not None:
                description = t.coroutine.__doc__
        t.description = " ".join(re.split(r"\n+\s*", description))
        # set a default title for human
        if not title:
            title = "".join([x.capitalize() for x in t.name.split("_")])
        t.title = title

    def wrapper(def_func: Callable) -> BaseTool:
        partial_ = tool(
            *args,
            return_direct=return_direct,
            args_schema=args_schema,
            infer_schema=infer_schema,
        )
        t = partial_(def_func)
        _parse_tool(t)
        return t

    if len(args) == 0:
        return wrapper
    else:
        t = tool(
            *args,
            return_direct=return_direct,
            args_schema=args_schema,
            infer_schema=infer_schema,
        )
        _parse_tool(t)
        return t


def format_context(self: BaseToolOutput) -> str:
    '''
    将包含知识库输出的ToolOutput格式化为 LLM 需要的字符串
    '''
    context = ""
    docs = self.data["docs"]
    source_documents = []

    for inum, doc in enumerate(docs):
        doc = DocumentWithVSId.parse_obj(doc)
        source_documents.append(doc.page_content)

    if len(source_documents) == 0:
        context = "没有找到相关文档,请更换关键词重试"
    else:
        for doc in source_documents:
            context += doc + "\n\n"

    return context
