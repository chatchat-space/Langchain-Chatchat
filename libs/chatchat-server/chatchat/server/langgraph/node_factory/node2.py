from typing import Dict,Any
from .nodes_registry import regist_nodes
from chatchat.server.pydantic_v1 import Field
#node2
@regist_nodes(title="节点2",description="这是节点2的描述")
def node2(*args: Any,**kwargs)-> Dict[str, any]:
    
    #通过关键字参数获取输入参数
    node2_input_1=kwargs["node2_input_1"]
    node2_input_2=kwargs["node2_input_2"]
    #打印参数
    print(f"node2_function: {node2_input_1},{node2_input_2}")
    #todo:节点2的业务逻辑
    

    #返回输出参数
    return {
        "node2_output_1":"这是节点2输出参数node2_output_1的值，会被存入全局state['state']中",
        "node2_output_2":"这是节点2输出参数node2_output_2的值，会被存入全局state['state']中"
        }