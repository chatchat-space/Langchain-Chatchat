from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union

from langchain.agents import tool
from langchain_core.tools import BaseTool

from chatchat.server.knowledge_base.kb_doc_api import DocumentWithVSId
from chatchat.server.pydantic_v1 import BaseModel, Extra


__all__ = ["regist_tool", "BaseToolOutput", "format_context"]


_TOOLS_REGISTRY = {}


# patch BaseTool to support extra fields e.g. a title
BaseTool.Config.extra = Extra.allow

################################### TODO: workaround to langchain #15855
# patch BaseTool to support tool parameters defined using pydantic Field


def _new_parse_input(
    self,
    tool_input: Union[str, Dict],
) -> Union[str, Dict[str, Any]]:
    """Convert tool input to pydantic model."""
    input_args = self.args_schema
    if isinstance(tool_input, str):
        if input_args is not None:
            key_ = next(iter(input_args.__fields__.keys()))
            input_args.validate({key_: tool_input})
        return tool_input
    else:
        if input_args is not None:
            result = input_args.parse_obj(tool_input)
            return result.dict()


def _new_to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
    # For backwards compatibility, if run_input is a string,
    # pass as a positional argument.
    if isinstance(tool_input, str):
        return (tool_input,), {}
    else:
        # for tool defined with `*args` parameters
        # the args_schema has a field named `args`
        # it should be expanded to actual *args
        # e.g.: test_tools
        #       .test_named_tool_decorator_return_direct
        #       .search_api
        if "args" in tool_input:
            args = tool_input["args"]
            if args is None:
                tool_input.pop("args")
                return (), tool_input
            elif isinstance(args, tuple):
                tool_input.pop("args")
                return args, tool_input
        return (), tool_input


BaseTool._parse_input = _new_parse_input
BaseTool._to_args_and_kwargs = _new_to_args_and_kwargs
###############################


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


class BaseToolOutput:
    """
    LLM 要求 Tool 的输出为 str，但 Tool 用在别处时希望它正常返回结构化数据。
    只需要将 Tool 返回值用该类封装，能同时满足两者的需要。
    基类简单的将返回值字符串化，或指定 format="json" 将其转为 json。
    用户也可以继承该类定义自己的转换方法。
    """

    def __init__(
        self,
        data: Any,
        format: str | Callable = None,
        data_alias: str = "",
        **extras: Any,
    ) -> None:
        self.data = data
        self.format = format
        self.extras = extras
        if data_alias:
            setattr(self, data_alias, property(lambda obj: obj.data))

    def __str__(self) -> str:
        if self.format == "json":
            return json.dumps(self.data, ensure_ascii=False, indent=2)
        elif callable(self.format):
            return self.format(self)
        else:
            return str(self.data)


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
