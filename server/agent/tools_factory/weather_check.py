"""
简单的单参数输入工具实现，用于查询现在天气的情况
"""
from server.pydantic_v1 import BaseModel, Field
import requests

def weather(location: str, api_key: str):
    url = f"https://api.seniverse.com/v3/weather/now.json?key={api_key}&location={location}&language=zh-Hans&unit=c"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = {
            "temperature": data["results"][0]["now"]["temperature"],
            "description": data["results"][0]["now"]["text"],
        }
        return weather
    else:
        raise Exception(
            f"Failed to retrieve weather: {response.status_code}")


def weather_check(location: str):
    return weather(location, "S8vrB4U_-c5mvAMiK")
class WeatherInput(BaseModel):
    location: str = Field(description="City name,include city and county,like '厦门'")
