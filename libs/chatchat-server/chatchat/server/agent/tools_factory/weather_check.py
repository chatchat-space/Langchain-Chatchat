"""
简单的单参数输入工具实现，用于查询现在天气的情况
"""
import requests

from chatchat.server.pydantic_v1 import Field
from chatchat.server.utils import get_tool_config

from .tools_registry import BaseToolOutput, regist_tool


@regist_tool(title="天气查询")
def weather_check(
    city: str = Field(description="City name,include city and county,like '厦门'"),
):
    """Use this tool to check the weather at a specific city"""

    tool_config = get_tool_config("weather_check")
    api_key = tool_config.get("api_key")
    url = f"https://api.seniverse.com/v3/weather/now.json?key={api_key}&location={city}&language=zh-Hans&unit=c"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = {
            "temperature": data["results"][0]["now"]["temperature"],
            "description": data["results"][0]["now"]["text"],
        }
        return BaseToolOutput(weather)
    else:
        raise Exception(f"Failed to retrieve weather: {response.status_code}")
