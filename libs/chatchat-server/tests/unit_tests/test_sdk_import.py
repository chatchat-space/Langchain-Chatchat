def test_sdk_import_unit():
    from langchain_chatchat import ChatPlatformAI, PlatformToolsRunnable


def test_mcp_import() -> None:
    """Test that the code can be imported"""
    from langchain_chatchat.agent_toolkits.mcp_kit import client, prompts, tools  # noqa: F401
