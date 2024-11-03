from typing import Dict, Any
from .nodes_registry import regist_nodes
from chatchat.server.utils import get_ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
#llm

default_system = """You are a chatbot,you can answer any question."""

@regist_nodes(title="LLM", description="大模型会话节点")
def llm(*args: Any, **kwargs) -> Dict[str, Any]:
    
    model_name = kwargs.get("model", "")
    temperature = kwargs.get("temperature", 0.1)
    prompt_template = kwargs.get("prompt_template", "")
    system = kwargs.get("system", default_system)
    llm = get_ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        streaming=False,
        local_wrap=False,
        verbose=True,
    )
    # Prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                prompt_template,
            ),
        ]
    )
    llm_bot = prompt | llm | StrOutputParser()
    # 获取线程执行的结果
    result = llm_bot.invoke(kwargs)
    print("llm",result)
    return {"answer":result}
