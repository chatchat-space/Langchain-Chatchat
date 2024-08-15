from typing import Dict,List,Callable,Any
from typing_extensions import TypedDict
from langgraph.graph import END, StateGraph, START
from langgraph.graph.graph import CompiledGraph
import importlib
from chatchat.server.langgraph import node_factory
importlib.reload(node_factory)
from chatchat.server.langgraph.node_factory.nodes_registry import _NODES_REGISTRY
class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        data: all state dict
    """
    #因为TypedDict很难动态构建，因此定义一个Dict类型state字段，用于保存所有langgraph的state
    state: Dict

#通用的全局state状态条件判断，用于判断全局state的某个字段是否满足某个条件,满足则返回设定的下一个节点的名称，可满足大部分使用场景
#复杂的添加判断，用户需自行添加代码实现
def wrapper_common_conditional(conditional_edge:Dict)->Callable:
    def common_conditional(state) -> str:
        condition = conditional_edge["condition"]
        for c in condition:
            refrence_state_name = c["refrence_state_name"]
            operator = c["operator"]
            value = c["value"]
            next_path = c["next_path"]
            if operator == "==":
                if state["state"][refrence_state_name] == value:
                    return next_path
            elif operator == "!=":
                if state["state"][refrence_state_name] != value:
                    return next_path
            elif operator == "in":
                if value in state["state"][refrence_state_name]:
                    return next_path
        return conditional_edge["default_path"]
    return common_conditional

def wrapper_state_function(node:Dict)->Callable:
    def do_node_function(state):
        nodel_name=node["name"]
        node_function=_NODES_REGISTRY[nodel_name]
        input_kwargs={}
        for arg in node["input_args"]:
            input_kwargs[arg["param_name"]]=state["state"][arg["value"]]

        return_value:Dict=node_function(**input_kwargs)

        output_kwargs={}
        for out_arg in node["output_args"]:
            output_kwargs[out_arg]=return_value[out_arg]

        #更新state["state"]状态，保留所有字段
        state["state"].update(output_kwargs)
        return {"state":state["state"]}
    return do_node_function


def build_flow(flow_params:Dict)->CompiledGraph:
    
    workflow = StateGraph(GraphState)
    
    #添加节点
    for node in flow_params["nodes"]:
        print("添加节点：",node["name"])
        workflow.add_node(node["name"], wrapper_state_function(node))
    #添加边
    for edge in flow_params["edges"]:
        print("添加边：",edge)
        workflow.add_edge(edge["from_node"], edge["to"])
    #添加条件边
    for conditional_edge in flow_params["conditional_edges"]:
        print("添加条件边：",conditional_edge)
        workflow.add_conditional_edges(conditional_edge["source"], wrapper_common_conditional(conditional_edge))
     # Compile
    app = workflow.compile()
    return app


# 测试样例数据
flow_params_example={
        "nodes": [
            {
                "name": "node1", 
                "input_args": [{"param_name":"question","type":"refrence","value":"question"}],
                "output_args": ["node1_output_1","node1_output_2"]
            },
            {
                "name": "node2", 
                "input_args": [
                    {"param_name":"node2_input_1","type":"refrence","value":"node1_output_1"},
                    {"param_name":"node2_input_2","type":"refrence","value":"node1_output_2"}
                ],
                "output_args": ["node2_output_1","node2_output_2"]
            },
            {
                "name": "node3", 
                "input_args": [
                    {"param_name":"node3_input_1","type":"refrence","value":"node2_output_1"},
                    {"param_name":"node3_input_2","type":"refrence","value":"node2_output_2"}
                ],
                "output_args": ["node3_output_1","node3_output_2"]
            },
            {
                "name": "node4", 
                "input_args": [
                    {"param_name":"node4_input_1","type":"refrence","value":"node2_output_1"},
                    {"param_name":"node4_input_2","type":"refrence","value":"node2_output_2"}
                ],
                "output_args": ["node4_output_1","node4_output_2"]
            }
        ],
        "edges": [
            {"from_node": "__start__", "to": "node1"},
            {"from_node": "node1", "to": "node2"},
            {"from_node": "node3", "to": "__end__"},
            {"from_node": "node4", "to": "__end__"}
        ],
        "conditional_edges": [
            {
                "source": "node2", "condition": [
                    #条件1，如果node2的输出参数1的值等于"这是节点2输出的参数1的值"，则进入node3
                    {
                        "refrence_state_name": "node2_output_1",
                        "operator": "==",
                        "value": "这是节点2输出的参数1的值",
                        "next_path": "node3"
                    },
                    #条件2，如果node2的输出参数1的值不等于"这是节点2输出的参数1的值"，则进入node4
                    {
                        "refrence_state_name": "node2_output_1",
                        "operator": "!=",
                        "value": "这是节点2输出的参数1的值",
                        "next_path": "node4"
                    },
                    #条件3，如果node2的输出参数2的值包含"finish"，则进入END节点
                    {
                        "refrence_state_name": "node2_output_2",
                        "operator": "in",
                        "value": "over",
                        "next_path": "__end__"
                    }                 
                ],
                #如果都不满足条件的默认节点
                "default_path": "__end__"
            }
        ]
    }

if __name__ == "__main__":
    app=build_flow(flow_params_example)
    inputs={"state":{"question":"这是问题"}}
    app.invoke(inputs)
    
#流式输出过程
# import rich
# import asyncio
# async def async_run_graph():
#     app=build_flow(flow_params_example)
#     inputs={"state":{"question":"这是问题"}}
#     async for e in app.astream_events(inputs, version="v2"):
#         rich.print('\n\n')
#         rich.print(e)
        
# if __name__ == "__main__":
#     asyncio.run(async_run_graph())


    
    