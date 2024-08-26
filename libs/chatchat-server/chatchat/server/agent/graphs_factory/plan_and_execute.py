import operator
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Annotated, Union, Optional, Tuple, Literal
from typing_extensions import TypedDict

from langchain import hub
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    ToolMessage,
    filter_messages,
)
from langchain_core.pydantic_v1 import BaseModel, Field
from langgraph.graph import StateGraph, START
from langgraph.graph.graph import CompiledGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition, create_react_agent

from chatchat.server.utils import get_graph_memory, build_logger
from .graphs_registry import regist_graph, InputHandler, EventHandler

logger = build_logger()


@dataclass
class Message:
    role: str
    content: str


class PlanAndExecuteInputHandler(InputHandler):
    def __init__(self):
        self.query = None
        self.metadata = None

    def create_inputs(self, query: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        self.query = query
        self.metadata = metadata
        return {"messages": asdict(Message(role="user", content=self.query))}
        # return {"input": query}


@dataclass
class Event:
    messages: List[BaseMessage]
    history: Optional[List[BaseMessage]] = None


class PlanAndExecuteEventHandler(EventHandler):
    def __init__(self):
        self.event = None

    def handle_event(self, event_data: Union[Event, Dict[str, Any]]) -> BaseMessage:
        '''
        event example:
        {
            'messages': [HumanMessage(
                            content='The youtube video of Xiao Yixian in Fights Break Sphere?',
                            id='b9c5468a-7340-425b-ae6f-2f584a961014')],
            'history': [HumanMessage(
                            content='The youtube video of Xiao Yixian in Fights Break Sphere?',
                            id='b9c5468a-7340-425b-ae6f-2f584a961014')]
        }
        '''
        if isinstance(event_data, dict):
            event = Event(
                messages=[BaseMessage(**msg.__dict__) for msg in event_data['messages']],
                history=[BaseMessage(**msg.__dict__) for msg in event_data.get('history', [])]
            )
        else:
            event = event_data
        return event.messages[0]


class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )


class Response(BaseModel):
    """Response to user."""

    response: str


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
                    "If you need to further use tools to get the answer, use Plan."
    )


class PlanStepExecuteResult(BaseModel):
    step: str
    result: str


class PlanExecute(BaseModel):
    messages: Annotated[list, add_messages]
    history: Optional[List[BaseMessage]] = None
    input: str
    plan: Optional[Plan] = None
    past_steps: Optional[List[PlanStepExecuteResult]] = None
    response: Optional[str] = None


@regist_graph(name="plan_and_execute",
              input_handler=PlanAndExecuteInputHandler,
              event_handler=PlanAndExecuteEventHandler)
def plan_and_execute(llm: ChatOpenAI, tools: list[BaseTool], history_len: int) -> CompiledGraph:
    if not isinstance(llm, ChatOpenAI):
        raise TypeError("llm must be an instance of ChatOpenAI")
    if not all(isinstance(tool, BaseTool) for tool in tools):
        raise TypeError("All items in tools must be instances of BaseTool")

    import rich  # debug

    memory = get_graph_memory()

    # Get the prompt to use - you can modify this!
    prompt = hub.pull("wfh/react-agent-executor")
    prompt.pretty_print()

    # Choose the LLM that will drive the agent
    agent_executor = create_react_agent(llm, tools, messages_modifier=prompt)

    async def history_manager(state: PlanExecute) -> PlanExecute:
        try:
            # 目的: 降本. 做法: 给 llm 传递历史上下文时, 把 Function Calling 相关内容过滤, 只保留 history_len 长度的历史上下文.
            # todo: """目前 history_len 直接截取了 messages 长度, 希望通过 对话轮数 来限制.
            #  原因: 一轮对话会追加数个 message, 但是目前没有从 snapshot(graph.get_state) 中找到很好的办法来获取一轮对话."""
            filtered_messages = []
            for message in filter_messages(state.messages, exclude_types=[ToolMessage]):
                if isinstance(message, AIMessage) and message.tool_calls:
                    continue
                filtered_messages.append(message)
            state.history = filtered_messages[-history_len-1:]
            return state
        except Exception as e:
            raise Exception(f"filtering messages error: {e}")

    planner_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """For the given objective, come up with a simple step by step plan. \
    This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
    The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.""",
            ),
            ("placeholder", "{messages}"),
        ]
    )
    planner = planner_prompt | llm.with_structured_output(Plan)

    async def plan_step(state: PlanExecute) -> PlanExecute:
        rich.print(f"\nplan_step 1: {state}\n")
        plan_list = await planner.ainvoke({"messages": state.history})
        plan = Plan(steps=plan_list.steps)
        state.plan = plan
        rich.print(f"\nplan_step 2: {state}\n")
        return state

    async def execute_step(state: PlanExecute) -> PlanExecute:
        rich.print(f"\nexecute_step 1: {state}\n")
        plan = state.plan
        plan_str = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(plan.steps))
        task = plan.steps[0]
        task_formatted = f"""For the following plan:
    {plan_str}\n\nYou are tasked with executing step {1}, {task}."""
        agent_response = await agent_executor.ainvoke(
            {"messages": [("user", task_formatted)]}
        )
        plan_step_execute_result = PlanStepExecuteResult(step=task, result=agent_response["messages"][-1].content)

        # Ensure past_steps is initialized
        if state.past_steps is None:
            state.past_steps = []

        state.past_steps.append(plan_step_execute_result)
        rich.print(f"\nexecute_step 2: {state}\n")
        return state

    replanner_prompt = ChatPromptTemplate.from_template(
        """For the given objective, come up with a simple step by step plan. \
    This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
    The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

    Your objective was this:
    {input}

    Your original plan was this:
    {plan}

    You have currently done the follow steps:
    {past_steps}

    Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with that. Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan."""
    )
    replanner = replanner_prompt | llm.with_structured_output(Act)

    async def replan_step(state: PlanExecute) -> PlanExecute:
        rich.print(f"\nreplan_step 1: {state}\n")
        # 将 PlanExecute 对象转换为字典
        # state_dict = state.dict()
        output = await replanner.ainvoke(state.dict())
        print(f"\nreplan_step output :{output}\n")
        if isinstance(output.action, Response):
            state.response = output.action.response
            state.messages = output.action.response
            state.history.append(AIMessage(output.action.response))
        else:
            plan = Plan(steps=output.action.steps)
            state.plan = plan
        rich.print(f"\nreplan_step2: {state}\n")
        return state

    def should_end(state: PlanExecute) -> Literal["agent", "__end__"]:
        # if "response" in state and state.response:
        if state.response:
            return "__end__"
        else:
            return "agent"

    graph_builder = StateGraph(PlanExecute)

    graph_builder.add_node("history_manager", history_manager)

    # Add the plan node
    graph_builder.add_node("planner", plan_step)

    # Add the execution step
    graph_builder.add_node("agent", execute_step)

    # Add a replan node
    graph_builder.add_node("replan", replan_step)

    graph_builder.add_edge(START, "history_manager")

    graph_builder.add_edge("history_manager", "planner")

    # From plan we go to agent
    graph_builder.add_edge("planner", "agent")

    # From agent, we replan
    graph_builder.add_edge("agent", "replan")

    graph_builder.add_conditional_edges(
        "replan",
        # Next, we pass in the function that will determine which node is called next.
        should_end,
    )

    # Finally, we compile it!
    # This compiles it into a LangChain Runnable,
    # meaning you can use it as you would any other runnable
    graph = graph_builder.compile(checkpointer=memory)

    return graph
