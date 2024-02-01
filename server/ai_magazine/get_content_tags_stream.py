from fastapi import Body
from fastapi.responses import StreamingResponse
from configs import LLM_MODELS, TEMPERATURE
from server.utils import wrap_done, get_ChatOpenAI
from langchain.chains import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from typing import AsyncIterable
import asyncio
from langchain.prompts.chat import ChatPromptTemplate
from typing import List
from server.chat.utils import History
from langchain.schema import BaseOutputParser
import re
from server.utils import get_prompt_template

majors = {
    "哲学": ["哲学类"],
    "经济学": ["经济学类","财政学类","金融学类","经济与贸易类"],
    "法学": ["法学类","政治学类","社会学类","民族学类","马克思主义理论类","公安学类"],
    "教育学": ["教育学类","体育学类"],
    "文学": ["中国语言文学类","外国语言文学类","新闻传播学类"],
    "历史学": ["历史学类"],
    "理学": ["数学类","物理学类","化学类","天文学类","地理科学类","大气科学类","海洋科学类","地球物理学类","地质学类","生物科学类","心理学类","统计学类"],
    "工学": ["力学类","机械类","仪器类","材料类","能源动力类","电气类","电子信息类","自动化类","计算机类","土木类","水利类","测绘类","化工与制药类","地质类","矿业类","纺织类","轻工类","交通运输类","海洋工程类","航空航天类","兵器类","核工程类","农业工程类","林业工程类","环境科学与工程类","生物医学工程类","食品科学与工程类","建筑类","安全科学与工程类","生物工程类","公安技术类","交叉工程类"],
    "农学": ["植物生产类","自然保护与环境生态类","动物生产类","动物医学类","林学类","水产类","草学类"],
    "医学": ["基础医学类","临床医学类","口腔医学类","公共卫生与预防医学类","中医学类","中西医结合类","药学类","中药学类","法医学类","医学技术类","护理学类"],
    "管理学": ["管理科学与工程类","工商管理类","农业经济管理类","公共管理类","图书情报与档案管理类","物流管理与工程类","工业工程类","电子商务类","旅游管理类","质量管理工程类","监狱学类"],
    "艺术学": ["艺术学理论类","音乐与舞蹈学类","戏剧与影视学类","美术学类","设计学类"]
}


async def get_content_tags_stream(query: str = Body(..., description="用户输入", examples=["恼羞成怒"]),
                history: List[History] = Body([],
                                       description="历史对话",
                                       examples=[[
                                           {"role": "user", "content": "我们来玩成语接龙，我先来，生龙活虎"},
                                           {"role": "assistant", "content": "虎头虎脑"}]]
                                       ),
                stream: bool = Body(False, description="流式输出"),
                model_name: str = Body(LLM_MODELS[0], description="LLM 模型名称。"),
                temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
                # top_p: float = Body(TOP_P, description="LLM 核采样。勿与temperature同时设置", gt=0.0, lt=1.0),
                prompt_name: str = Body("llm_chat", description="使用的prompt模板名称(在configs/prompt_config.py中配置)"),
                content: str = Body(..., description="文章内容"),
         ):
    history = []
    
    target_major = "无"
    
        
    # 返回模版
    ret = {
        "answer": "暂时无法回答该问题",
        "docs": "",
        "question_type": ""
    }

    async def get_content_tags_iterator(query: str,
                            history: List[History] = [],
                            model_name: str = LLM_MODELS[0],
                            prompt_name: str = prompt_name,
                            content: str = content,
                            ) -> AsyncIterable[str]:
        callback = AsyncIteratorCallbackHandler()
        model = get_ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            callbacks=[callback],
        )
        
        if query == '内容':
            prompt_template = get_prompt_template("llm_tag","default")
        else:
            if '_' in query:
                print("二级标签prompt")
                prompt_template = get_prompt_template("llm_tag_major_2","default")
                target_major = query.split('_')[1]
                print('一级标签：', query.split('_')[0], '候选二级标签：', majors[target_major])
            else:
                print("一级标签prompt")
                prompt_template = get_prompt_template("llm_tag_major","default")
                
        print("prompt_template:", prompt_template)
        input_msg = History(role="user", content=prompt_template).to_msg_template(False)
        chat_prompt = ChatPromptTemplate.from_messages(
            [i.to_msg_template() for i in history] + [input_msg])
        chain = LLMChain(prompt=chat_prompt, llm=model)

        # Begin a task that runs in the background.
        if query.startswith("2级专业"):
            task = asyncio.create_task(wrap_done(
                chain.acall({"content":content, "tags": ','.join(majors[target_major])}),
                callback.done),
            )
        else:
            task = asyncio.create_task(wrap_done(
                chain.acall({"content":content}),
                callback.done),
            )

        if stream:
            async for token in callback.aiter():
                # Use server-sent-events to stream the response
                yield token
        else:
            answer = ""
            async for token in callback.aiter():
                answer += token
            yield answer

        await task  

    return StreamingResponse(get_content_tags_iterator(query=query,
                                           history=history,
                                           model_name=model_name,
                                           prompt_name=prompt_name),
                             media_type="text/event-stream")

