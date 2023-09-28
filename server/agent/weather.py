## 使用和风天气API查询天气
from __future__ import annotations

## 单独运行的时候需要添加
import sys
import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


from server.utils import get_ChatOpenAI


import re
import warnings
from typing import Dict

from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.pydantic_v1 import Extra, root_validator
from langchain.schema import BasePromptTemplate
from langchain.schema.language_model import BaseLanguageModel
import requests
from typing import List, Any, Optional
from configs.model_config import LLM_MODEL, TEMPERATURE

## 使用和风天气API查询天气
KEY = ""

def get_city_info(location, adm, key):
    base_url = 'https://geoapi.qweather.com/v2/city/lookup?'
    params = {'location': location, 'adm': adm, 'key': key}
    response = requests.get(base_url, params=params)
    data = response.json()
    return data


from datetime import datetime


def format_weather_data(data):
    hourly_forecast = data['hourly']
    formatted_data = ''
    for forecast in hourly_forecast:
        # 将预报时间转换为datetime对象
        forecast_time = datetime.strptime(forecast['fxTime'], '%Y-%m-%dT%H:%M%z')
        # 获取预报时间的时区
        forecast_tz = forecast_time.tzinfo
        # 获取当前时间（使用预报时间的时区）
        now = datetime.now(forecast_tz)
        # 计算预报日期与当前日期的差值
        days_diff = (forecast_time.date() - now.date()).days
        if days_diff == 0:
            forecast_date_str = '今天'
        elif days_diff == 1:
            forecast_date_str = '明天'
        elif days_diff == 2:
            forecast_date_str = '后天'
        else:
            forecast_date_str = str(days_diff) + '天后'
        forecast_time_str = forecast_date_str + ' ' + forecast_time.strftime('%H:%M')
        # 计算预报时间与当前时间的差值
        time_diff = forecast_time - now
        # 将差值转换为小时
        hours_diff = time_diff.total_seconds() // 3600
        if hours_diff < 1:
            hours_diff_str = '1小时后'
        elif hours_diff >= 24:
            # 如果超过24小时，转换为天数
            days_diff = hours_diff // 24
            hours_diff_str = str(int(days_diff)) + '天后'
        else:
            hours_diff_str = str(int(hours_diff)) + '小时后'
        # 将预报时间和当前时间的差值添加到输出中
        formatted_data += '预报时间: ' + hours_diff_str + '\n'
        formatted_data += '具体时间: ' + forecast_time_str + '\n'
        formatted_data += '温度: ' + forecast['temp'] + '°C\n'
        formatted_data += '天气: ' + forecast['text'] + '\n'
        formatted_data += '风向: ' + forecast['windDir'] + '\n'
        formatted_data += '风速: ' + forecast['windSpeed'] + '级\n'
        formatted_data += '湿度: ' + forecast['humidity'] + '%\n'
        formatted_data += '降水概率: ' + forecast['pop'] + '%\n'
        # formatted_data += '降水量: ' + forecast['precip'] + 'mm\n'
        formatted_data += '\n\n'
    return formatted_data


def get_weather(key, location_id, time: str = "24"):
    if time:
        url = "https://devapi.qweather.com/v7/weather/" + time + "h?"
    else:
        time = "3"  # 免费订阅只能查看3天的天气
        url = "https://devapi.qweather.com/v7/weather/" + time + "d?"
    params = {
        'location': location_id,
        'key': key,
    }
    response = requests.get(url, params=params)
    data = response.json()
    return format_weather_data(data)


def split_query(query):
    parts = query.split()
    location = parts[0] if parts[0] != 'None' else parts[1]
    adm = parts[1]
    time = parts[2]
    return location, adm, time


def weather(query):
    location, adm, time = split_query(query)
    key = KEY
    if time != "None" and int(time) > 24:
        return "只能查看24小时内的天气，无法回答"
    if time == "None":
        time = "24"  # 免费的版本只能24小时内的天气
    if key == "":
        return "请先在代码中填入和风天气API Key"
    city_info = get_city_info(location=location, adm=adm, key=key)
    location_id = city_info['location'][0]['id']
    weather_data = get_weather(key=key, location_id=location_id, time=time)
    return weather_data


class LLMWeatherChain(Chain):
    llm_chain: LLMChain
    llm: Optional[BaseLanguageModel] = None
    """[Deprecated] LLM wrapper to use."""
    prompt: BasePromptTemplate
    """[Deprecated] Prompt to use to translate to python if necessary."""
    input_key: str = "question"  #: :meta private:
    output_key: str = "answer"  #: :meta private:

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def raise_deprecation(cls, values: Dict) -> Dict:
        if "llm" in values:
            warnings.warn(
                "Directly instantiating an LLMWeatherChain with an llm is deprecated. "
                "Please instantiate with llm_chain argument or using the from_llm "
                "class method."
            )
            if "llm_chain" not in values and values["llm"] is not None:
                prompt = values.get("prompt", PROMPT)
                values["llm_chain"] = LLMChain(llm=values["llm"], prompt=prompt)
        return values

    @property
    def input_keys(self) -> List[str]:
        """Expect input key.

        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Expect output key.

        :meta private:
        """
        return [self.output_key]

    def _evaluate_expression(self, expression: str) -> str:
        try:
            output = weather(expression)
        except Exception as e:
            output = "输入的信息有误，请再次尝试"
            # raise ValueError(f"错误: {expression}，输入的信息不对")

        return output

    def _process_llm_result(
            self, llm_output: str, run_manager: CallbackManagerForChainRun
    ) -> Dict[str, str]:

        run_manager.on_text(llm_output, color="green", verbose=self.verbose)

        llm_output = llm_output.strip()
        text_match = re.search(r"^```text(.*?)```", llm_output, re.DOTALL)
        if text_match:
            expression = text_match.group(1)
            output = self._evaluate_expression(expression)
            run_manager.on_text("\nAnswer: ", verbose=self.verbose)
            run_manager.on_text(output, color="yellow", verbose=self.verbose)
            answer = "Answer: " + output
        elif llm_output.startswith("Answer:"):
            answer = llm_output
        elif "Answer:" in llm_output:
            answer = "Answer: " + llm_output.split("Answer:")[-1]
        else:
            raise ValueError(f"unknown format from LLM: {llm_output}")
        return {self.output_key: answer}

    async def _aprocess_llm_result(
            self,
            llm_output: str,
            run_manager: AsyncCallbackManagerForChainRun,
    ) -> Dict[str, str]:
        await run_manager.on_text(llm_output, color="green", verbose=self.verbose)
        llm_output = llm_output.strip()
        text_match = re.search(r"^```text(.*?)```", llm_output, re.DOTALL)
        if text_match:
            expression = text_match.group(1)
            output = self._evaluate_expression(expression)
            await run_manager.on_text("\nAnswer: ", verbose=self.verbose)
            await run_manager.on_text(output, color="yellow", verbose=self.verbose)
            answer = "Answer: " + output
        elif llm_output.startswith("Answer:"):
            answer = llm_output
        elif "Answer:" in llm_output:
            answer = "Answer: " + llm_output.split("Answer:")[-1]
        else:
            raise ValueError(f"unknown format from LLM: {llm_output}")
        return {self.output_key: answer}

    def _call(
            self,
            inputs: Dict[str, str],
            run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        _run_manager.on_text(inputs[self.input_key])
        llm_output = self.llm_chain.predict(
            question=inputs[self.input_key],
            stop=["```output"],
            callbacks=_run_manager.get_child(),
        )
        return self._process_llm_result(llm_output, _run_manager)

    async def _acall(
            self,
            inputs: Dict[str, str],
            run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        _run_manager = run_manager or AsyncCallbackManagerForChainRun.get_noop_manager()
        await _run_manager.on_text(inputs[self.input_key])
        llm_output = await self.llm_chain.apredict(
            question=inputs[self.input_key],
            stop=["```output"],
            callbacks=_run_manager.get_child(),
        )
        return await self._aprocess_llm_result(llm_output, _run_manager)

    @property
    def _chain_type(self) -> str:
        return "llm_weather_chain"

    @classmethod
    def from_llm(
            cls,
            llm: BaseLanguageModel,
            prompt: BasePromptTemplate,
            **kwargs: Any,
    ) -> LLMWeatherChain:
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        return cls(llm_chain=llm_chain, **kwargs)


from langchain.prompts import PromptTemplate

_PROMPT_TEMPLATE = """用户将会向您咨询天气问题，您不需要自己回答天气问题，而是将用户提问的信息提取出来区，市和时间三个元素后使用我为你编写好的工具进行查询并返回结果，格式为 区+市+时间 每个元素用空格隔开。如果缺少信息，则用 None 代替。
问题: ${{用户的问题}}

```text

${{拆分的区，市和时间}}
```

... weather(提取后的关键字，用空格隔开)...
```output

${{提取后的答案}}
```
答案: ${{答案}}

这是两个例子：
问题: 上海浦东未来1小时天气情况？

```text
浦东 上海 1
```
...weather(浦东 上海 1)...

```output

预报时间: 1小时后
具体时间: 今天 18:00
温度: 24°C
天气: 多云
风向: 西南风
风速: 7级
湿度: 88%
降水概率: 16%

Answer: 
预报时间: 1小时后
具体时间: 今天 18:00
温度: 24°C
天气: 多云
风向: 西南风
风速: 7级
湿度: 88%
降水概率: 16%

问题: 北京市朝阳区未来24小时天气如何？
```text

朝阳 北京 24
```
...weather(朝阳 北京 24)...
```output
预报时间: 23小时后
具体时间: 明天 17:00
温度: 26°C
天气: 霾
风向: 西南风
风速: 11级
湿度: 65%
降水概率: 20%
Answer:
预报时间: 23小时后
具体时间: 明天 17:00
温度: 26°C
天气: 霾
风向: 西南风
风速: 11级
湿度: 65%
降水概率: 20%

现在，这是我的问题：
问题: {question}
"""
PROMPT = PromptTemplate(
    input_variables=["question"],
    template=_PROMPT_TEMPLATE,
)


def weathercheck(query: str):
    model = get_ChatOpenAI(
        streaming=False,
        model_name=LLM_MODEL,
        temperature=TEMPERATURE,
    )
    llm_weather = LLMWeatherChain.from_llm(model, verbose=True, prompt=PROMPT)
    ans = llm_weather.run(query)
    return ans

if __name__ == '__main__':

    ## 检测api是否能正确返回
    query = "上海浦东未来1小时天气情况"
    # ans = weathercheck(query)
    ans = weather("浦东 上海 1")
    print(ans)