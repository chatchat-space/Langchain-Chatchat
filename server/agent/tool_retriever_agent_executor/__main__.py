from langchain.llms import OpenAI
from server.agent.tool_retriever_agent_executor import define_tools_retriever, RetrievalToolExecutor

import langchain
langchain.verbose = True

if __name__ == "__main__":
    """
        在线api目前不支持认证，
        可通过以下方式兼容
        OpenAPIEndpointChain 增加一个属性，初始化的时候，把属性传给 NLAToolkit.from_llm_and_ai_plugin，
        往后的调用链是from_llm_and_spec->>_get_http_operation_tools>> NLATool.from_llm_and_method
        NLATool.from_llm_and_method负责创建NLATool构件，里面有个OpenAPIEndpointChain基础包，这个包不支持auth，
        所以需要把创建的属性加载到这个OpenAPIEndpointChain里，在_call方法执行的时候，运行认证逻辑 
        OpenAPIEndpointChain改这个类的初始化和运行的代码就可以了
        你也可以去langchain的github上提issue，让他们支持auth
        不过langchain貌似没有定义认证类的core，所以，这样横跨几个模块的pr，估计他们不给通过
    """
    import sys
    import asyncio

    if sys.version_info < (3, 10):
        loop = asyncio.get_event_loop()
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)
    # 同步调用协程代码
    retriever, toolkits_dict = loop.run_until_complete(define_tools_retriever())
    # 构建工具执行器
    toolkits_executor = RetrievalToolExecutor.from_retriever_and_toolkits_dict(
        retriever=retriever, toolkits_dict=toolkits_dict
    )
    llm = OpenAI(temperature=0)
    # 初始化代理执行器，选取合适的工具
    agent_executor = toolkits_executor.build_executor("cos(x)-sin(2x^2)=0有没有解?", llm)

    # 执行代理
    result = agent_executor.run("cos(x)-sin(2x^2)=0有没有解?cos(x)-sin(2x^2)=0有没有解?")

    print(result)
