import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from server.utils import get_ChatOpenAI
from server.agent.tools_factory.tools_registry import all_tools
from server.agent.agent_factory.qwen_agent import initialize_qwen_agent
from langchain import globals

globals.set_debug(True)
globals.set_verbose(True)


qwen_model = get_ChatOpenAI("Qwen-1_8B-Chat", 0.01, streaming=False)
executor = initialize_qwen_agent(tools=all_tools, llm=qwen_model)

# ret = executor.invoke("苏州今天冷吗")
ret = executor.invoke("从知识库samples中查询chatchat项目简介")
# ret = executor.invoke("chatchat项目主要issue有哪些")
print(ret)
