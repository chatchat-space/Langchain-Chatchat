"""
source  https://github.com/langchain-ai/langchain-mcp-adapters
"""
from typing import Any, Type, Dict
import inspect
from mcp.server.fastmcp.utilities.func_metadata import ArgModelBase

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
from pydantic.v1 import BaseModel, create_model, Field
from pydantic.v1.fields import FieldInfo

NonTextContent = ImageContent | EmbeddedResource


class MCPStructuredTool(StructuredTool):
    server_name: str


def schema_dict_to_model(schema: Dict[str, Any]) -> Any:
    fields = schema.get('properties', {})
    required_fields = schema.get('required', [])

    model_fields = {}
    for field_name, details in fields.items():
        field_type_str = details['type']

        if field_type_str == 'integer':
            field_type = int
        elif field_type_str == 'string':
            field_type = str
        elif field_type_str == 'number':
            field_type = float
        elif field_type_str == 'boolean':
            field_type = bool
        else:
            field_type = Any  # 可扩展更多类型

        if field_name in required_fields:
            model_fields[field_name] = (field_type, ...)
        else:
            model_fields[field_name] = (field_type, None)

    DynamicSchema = create_model(schema.get('title', 'DynamicSchema'), **model_fields)
    return DynamicSchema


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
        server_name: str,
        session: ClientSession,
        tool: MCPTool,
) -> BaseTool:
    """Convert an MCP tool to a LangChain tool.

    NOTE: this tool can be executed only in a context of an active MCP client session.

    Args:
        server_name: MCP server name
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
    return MCPStructuredTool(
        server_name=server_name,
        name=tool.name,
        description=tool.description or "",
        args_schema=tool_input_model,
        coroutine=call_tool,
        response_format="content_and_artifact",
    )


async def load_mcp_tools(server_name: str, session: ClientSession) -> list[BaseTool]:
    """Load all available MCP tools and convert them to LangChain tools."""
    tools = await session.list_tools()
    return [convert_mcp_tool_to_langchain_tool(server_name, session, tool) for tool in tools.tools]
