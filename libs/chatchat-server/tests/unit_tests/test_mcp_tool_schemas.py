from unittest.mock import AsyncMock

import pytest
from mcp.types import CallToolResult, TextContent, Tool
from pydantic.v1 import ValidationError

from langchain_chatchat.agent_toolkits.mcp_kit.tools import (
    convert_mcp_tool_to_langchain_tool,
    schema_dict_to_model,
)


@pytest.mark.asyncio
async def test_tool_with_nullable_schema_preserves_arguments():
    session = AsyncMock()
    session.call_tool.return_value = CallToolResult(
        content=[TextContent(type="text", text='{"results": []}')]
    )
    tool = convert_mcp_tool_to_langchain_tool(
        "remote",
        session,
        Tool(
            name="search",
            inputSchema={
                "type": "object",
                "properties": {
                    "queries": {"type": "array", "items": {"type": "string"}},
                    "context": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                },
                "required": ["queries"],
            },
        ),
    )

    for arguments in (
        {"queries": ["Python docs"]},
        {"queries": ["Python docs"], "context": None},
        {"queries": ["Python docs"], "context": "official sources"},
    ):
        assert await tool.ainvoke(arguments) == '{"results": []}'
        session.call_tool.assert_awaited_with("search", arguments)


def test_untyped_required_field_is_still_required():
    schema = schema_dict_to_model(
        {
            "properties": {"value": {"description": "Any JSON value"}},
            "required": ["value"],
        }
    )
    assert schema(value={"nested": [1, "two"]}).value == {"nested": [1, "two"]}
    with pytest.raises(ValidationError):
        schema()


@pytest.mark.parametrize("arguments", [{}, {"query": ""}])
def test_required_string_validation_is_preserved(arguments):
    schema = schema_dict_to_model(
        {
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        }
    )
    with pytest.raises(ValidationError):
        schema(**arguments)
