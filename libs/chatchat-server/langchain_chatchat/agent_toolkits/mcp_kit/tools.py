"""
source  https://github.com/langchain-ai/langchain-mcp-adapters
"""
from typing import Any, Type, Dict
import inspect
from mcp.server.fastmcp.utilities.func_metadata import ArgModelBase
from pydantic import BaseModel, create_model, Field
from langchain_core.tools import BaseTool, StructuredTool, ToolException
from mcp import ClientSession
from mcp.types import (
    CallToolResult,
    EmbeddedResource,
    ImageContent,
    TextContent,
)
from mcp.types import (
    Tool as MCPTool,
)
from pydantic.fields import FieldInfo

NonTextContent = ImageContent | EmbeddedResource

from typing import Any, Type
from pydantic import BaseModel, Field, create_model


def schema_dict_to_model(schema: dict) -> Type[BaseModel]:
    dynamic_pydantic_model_params = {}
    for name, prop in schema.get("properties", {}).items():
        # 简化类型映射
        type_str = prop.get("type", "string")
        if type_str == "integer":
            py_type = int
        elif type_str == "number":
            py_type = float
        elif type_str == "boolean":
            py_type = bool
        elif type_str == "array":
            py_type = list
        elif type_str == "object":
            py_type = dict
        else:
            py_type = str

        default = ... if name in schema.get("required", []) else None
        field_info = FieldInfo.from_annotated_attribute(
            py_type,
            inspect.Parameter.empty
        )
        dynamic_pydantic_model_params[name] = (field_info.annotation, field_info)

    model_name = schema.get("title", "DynamicModel")
    return create_model(model_name,
                        **dynamic_pydantic_model_params,
                        __base__=BaseModel)


def _convert_call_tool_result(
        call_tool_result: CallToolResult,
) -> tuple[str | list[str], list[NonTextContent] | None]:
    text_contents: list[TextContent] = []
    non_text_contents = []
    for content in call_tool_result.content:
        if isinstance(content, TextContent):
            text_contents.append(content)
        else:
            non_text_contents.append(content)

    tool_content: str | list[str] = [content.text for content in text_contents]
    if len(text_contents) == 1:
        tool_content = tool_content[0]

    if call_tool_result.isError:
        raise ToolException(tool_content)

    return tool_content, non_text_contents or None


def convert_mcp_tool_to_langchain_tool(
        session: ClientSession,
        tool: MCPTool,
) -> BaseTool:
    """Convert an MCP tool to a LangChain tool.

    NOTE: this tool can be executed only in a context of an active MCP client session.

    Args:
        session: MCP client session
        tool: MCP tool to convert

    Returns:
        a LangChain tool
    """

    async def call_tool(
            **arguments: dict[str, Any],
    ) -> tuple[str | list[str], list[NonTextContent] | None]:
        call_tool_result = await session.call_tool(tool.name, arguments)
        return _convert_call_tool_result(call_tool_result)

    tool_input_model = schema_dict_to_model(tool.inputSchema)
    return StructuredTool(
        name=tool.name,
        description=tool.description or "",
        args_schema=tool_input_model,
        coroutine=call_tool,
        response_format="content_and_artifact",
    )


async def load_mcp_tools(session: ClientSession) -> list[BaseTool]:
    """Load all available MCP tools and convert them to LangChain tools."""
    tools = await session.list_tools()
    return [convert_mcp_tool_to_langchain_tool(session, tool) for tool in tools.tools]
