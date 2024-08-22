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


class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str


@regist_graph(name="plan_and_execute",
              input_handler=PlanAndExecuteInputHandler,
              event_handler=PlanAndExecuteEventHandler)
def plan_and_execute(llm: ChatOpenAI, tools: list[BaseTool], history_len: int) -> CompiledGraph:
    if not isinstance(llm, ChatOpenAI):
        raise TypeError("llm must be an instance of ChatOpenAI")
    if not all(isinstance(tool, BaseTool) for tool in tools):
        raise TypeError("All items in tools must be instances of BaseTool")

    memory = get_graph_memory()

    # Get the prompt to use - you can modify this!
    prompt = hub.pull("wfh/react-agent-executor")
    prompt.pretty_print()

    # Choose the LLM that will drive the agent
    agent_executor = create_react_agent(llm, tools, messages_modifier=prompt)

    class Plan(BaseModel):
        """Plan to follow in future"""

        steps: List[str] = Field(
            description="different steps to follow, should be in sorted order"
        )

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

    class Response(BaseModel):
        """Response to user."""

        response: str

    class Act(BaseModel):
        """Action to perform."""

        action: Union[Response, Plan] = Field(
            description="Action to perform. If you want to respond to user, use Response. "
                        "If you need to further use tools to get the answer, use Plan."
        )

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

    async def execute_step(state: PlanExecute):
        plan = state["plan"]
        plan_str = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(plan))
        task = plan[0]
        task_formatted = f"""For the following plan:
    {plan_str}\n\nYou are tasked with executing step {1}, {task}."""
        agent_response = await agent_executor.ainvoke(
            {"messages": [("user", task_formatted)]}
        )
        return {
            "past_steps": (task, agent_response["messages"][-1].content),
        }

    async def plan_step(state: PlanExecute):
        plan = await planner.ainvoke({"messages": [("user", state["input"])]})
        return {"plan": plan.steps}

    async def replan_step(state: PlanExecute):
        output = await replanner.ainvoke(state)
        if isinstance(output.action, Response):
            return {"response": output.action.response}
        else:
            return {"plan": output.action.steps}

    def should_end(state: PlanExecute) -> Literal["agent", "__end__"]:
        if "response" in state and state["response"]:
            return "__end__"
        else:
            return "agent"

    graph_builder = StateGraph(PlanExecute)

    # Add the plan node
    graph_builder.add_node("planner", plan_step)

    # Add the execution step
    graph_builder.add_node("agent", execute_step)

    # Add a replan node
    graph_builder.add_node("replan", replan_step)

    graph_builder.add_edge(START, "planner")

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
