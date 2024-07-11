import requests
from chatchat.server.pydantic_v1 import Field
from .tools_registry import BaseToolOutput, regist_tool
from chatchat.server.utils import get_tool_config

BASE_URL = "https://restapi.amap.com/v5/place/text"

def amap_poi_search_engine(keywords: str,types: str,config: dict):
    API_KEY = config["api_key"]
    params = {
        "keywords": keywords,
        "types": types,
        "key": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "API request failed"}



@regist_tool(title="高德地图POI搜索")
def amap_poi_search(location: str = Field(description="'实际地名'或者'具体的地址',不能使用简称或者别称"),
                types: str = Field(description="POI类型，比如商场、学校、医院等等")):
    """ A wrapper that uses Amap to search."""
    tool_config = get_tool_config("amap")
    return BaseToolOutput(amap_poi_search_engine(keywords=location,types=types,config=tool_config))
