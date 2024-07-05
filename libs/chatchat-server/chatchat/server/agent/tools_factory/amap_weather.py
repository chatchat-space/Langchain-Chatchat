import requests
from chatchat.server.pydantic_v1 import Field
from .tools_registry import BaseToolOutput, regist_tool
from chatchat.server.utils import get_tool_config

BASE_DISTRICT_URL = "https://restapi.amap.com/v3/config/district"
BASE_WEATHER_URL = "https://restapi.amap.com/v3/weather/weatherInfo"

def get_adcode(city: str, config: dict) -> str:
    """Get the adcode"""
    API_KEY = config["api_key"]
    params = {
        "keywords": city,
        "subdistrict": 0, 
        "extensions": "base",
        "key": API_KEY
    }
    response = requests.get(BASE_DISTRICT_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["districts"][0]["adcode"]
    else:
        return None

def get_weather(adcode: str, config: dict) -> dict:
    """Get  weather information."""
    API_KEY = config["api_key"]
    params = {
        "city": adcode,
        "extensions": "all",
        "key": API_KEY
    }
    response = requests.get(BASE_WEATHER_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "API request failed"}

@regist_tool(title="高德地图天气查询")
def amap_weather(city: str = Field(description="城市名")):
    """A wrapper that uses Amap to get weather information."""
    tool_config = get_tool_config("amap")
    adcode = get_adcode(city, tool_config)
    if adcode:
        weather_data = get_weather(adcode, tool_config)
        return BaseToolOutput(weather_data)
    else:
        return BaseToolOutput({"error": "无法获取城市编码"})

