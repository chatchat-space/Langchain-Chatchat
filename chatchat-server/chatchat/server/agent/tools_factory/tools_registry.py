import re
from typing import Any, Union, Dict, Tuple, Callable, Optional, Type

from langchain.agents import tool
from langchain_core.tools import BaseTool

from chatchat.server.pydantic_v1 import BaseModel


_TOOLS_REGISTRY = {}


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
    description: str = "",
    return_direct: bool = False,
    args_schema: Optional[Type[BaseModel]] = None,
    infer_schema: bool = True,
) -> Union[Callable, BaseTool]:
    '''
    wrapper of langchain tool decorator
    add tool to regstiry automatically
    '''
    def _parse_tool(t: BaseTool):
        nonlocal description

        _TOOLS_REGISTRY[t.name] = t
        # change default description
        if not description:
            if t.func is not None:
                description = t.func.__doc__
            elif t.coroutine is not None:
                description = t.coroutine.__doc__ 
        t.description = " ".join(re.split(r"\n+\s*", description))

    def wrapper(def_func: Callable) -> BaseTool:
        partial_ = tool(*args,
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
        t = tool(*args,
                return_direct=return_direct,
                args_schema=args_schema,
                infer_schema=infer_schema,
                )
        _parse_tool(t)
        return t
