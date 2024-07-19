"""
通过jina-ai/reader项目，将url内容处理为llm易于理解的文本形式
"""
import requests

import re

from chatchat.server.pydantic_v1 import Field
from chatchat.server.utils import get_tool_config

from chatchat.server.agent.tools_factory.tools_registry import format_context

from .tools_registry import BaseToolOutput, regist_tool


@regist_tool(title="URL内容阅读")
def url_reader(
        url: str = Field(
            description="The URL to be processed, so that its web content can be made more clear to read. Then provide a detailed description of the content in about 500 words. As structured as possible. ONLY THE LINK SHOULD BE PASSED IN."),
):
    """Use this tool to get the clear content of a URL."""

    tool_config = get_tool_config("url_reader")
    timeout = tool_config.get("timeout")

    # 提取url文本中的网页链接部分。url文本可能是一句话
    url_pattern = r'http[s]?://[a-zA-Z0-9./?&=_%#-]+'
    match = re.search(url_pattern, url)
    url = match.group(0) if match else None

    if url is None:
        return BaseToolOutput({"error": "No URL"})

    reader_url = "https://r.jina.ai/{url}".format(url=url)

    response = requests.get(reader_url, timeout=timeout)

    if response.status_code == 200:
        return BaseToolOutput(
            {"result": response.text, "docs": [{"page_content": response.text, "metadata": {'source': url, 'id': ''}}]},
            format=format_context)
    else:
        return BaseToolOutput({"error": "Timeout"})
