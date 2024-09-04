import sys
import rich
import datetime
from typing import List, Any, Union, Optional, Literal

from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field, ValidationError
from langchain_core.tools import StructuredTool
from langchain_core.tools import BaseTool
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.graph import CompiledGraph
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_openai.chat_models import ChatOpenAI

from chatchat.server.utils import get_graph_memory, build_logger
from .graphs_registry import regist_graph, InputHandler, EventHandler, State, async_history_manager

logger = build_logger()


class Reflection(BaseModel):
    missing: str = Field(description="Critique of what is missing.")
    superfluous: str = Field(description="Critique of what is superfluous")


class AnswerQuestion(BaseModel):
    """Answer the question. Provide an answer, reflection, and then follow up with search queries to improve the answer."""

    answer: str = Field(description="~250 word detailed answer to the question.")
    reflection: Reflection = Field(description="Your reflection on the initial answer.")
    search_queries: List[str] = Field(
        description="1-3 search queries for researching improvements to address the critique of your current answer."
    )


# Extend the initial answer schema to include references.
# Forcing citation in the model encourages grounded responses
class ReviseAnswer(AnswerQuestion):
    """Revise your original answer to your question. Provide an answer, reflection,

    cite your reflection with references, and finally
    add search queries to improve the answer."""

    references: List[str] = Field(
        description="Citations motivating your updated answer."
    )


class ResponderWithRetries:
    def __init__(self, runnable, validator):
        self.runnable = runnable
        self.validator = validator

    def respond(self, state: State) -> State:
        messages = state["messages"]
        print(f"Responding with {len(messages)}")
        validation_error_count = 0  # 初始化计数器
        count = 3
        for attempt in range(count):
            response = self.runnable.invoke(
                {"messages": messages},
                {"tags": [f"attempt:{attempt}"]}
            )

            try:
                validator_response = self.validator.invoke(response)

                # print(f"\n  ✅✅✅✅  respond state finally_response:")
                # rich.print(response)

                state["messages"] = response
                return state
            except ValidationError as e:
                validation_error_count += 1  # 增加计数器
                print(f"validation_error_count: {validation_error_count}")

                if validation_error_count >= count:  # 检查计数器是否达到上限
                    print(f"\n  ❌❌❌❌  Maximum validation errors reached. Exiting.")
                    sys.exit(1)  # 直接停止流程，不再继续

                content = (f"{repr(e)}"
                           f"Pay close attention to the function schema."
                           f"{self.validator.schema_json()}"
                           f"Respond by fixing all validation errors.")
                if validation_error_count >= 2:
                    # 避免第一轮对话时, messages[-1] 是 HumanMessage
                    if content == messages[-1].content:
                        continue
                else:
                    messages = messages + [
                        response,
                        ToolMessage(
                            content=content,
                            tool_call_id=response.tool_calls[0]["id"],
                        ),
                    ]
                    print(f"\n  ❌❌❌  respond ValidationError messages:")
                    rich.print(messages[-1].content)


class ReflexionEventHandler(EventHandler):
    def __init__(self):
        pass

    def handle_event(self, node: str, events: State) -> BaseMessage:
        """
        event example:
        {
            'messages': [HumanMessage(
                            content='The youtube video of Xiao Yixian in Fights Break Sphere?',
                            id='b9c5468a-7340-425b-ae6f-2f584a961014')],
            'history': [HumanMessage(
                            content='The youtube video of Xiao Yixian in Fights Break Sphere?',
                            id='b9c5468a-7340-425b-ae6f-2f584a961014')]
        }
        """
        return events["messages"][0]


@regist_graph(name="reflexion",
              input_handler=InputHandler,
              event_handler=ReflexionEventHandler)
def reflexion(llm: ChatOpenAI, tools: list[BaseTool], history_len: int) -> CompiledGraph:
    """
    description: https://langchain-ai.github.io/langgraph/tutorials/reflexion/reflexion/
    """
    if not isinstance(llm, ChatOpenAI):
        raise TypeError("llm must be an instance of ChatOpenAI")
    if not all(isinstance(tool, BaseTool) for tool in tools):
        raise TypeError("All items in tools must be instances of BaseTool")

    memory = get_graph_memory()

    search_internet = DuckDuckGoSearchResults(max_results=5)
    
    actor_prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are expert researcher.
    Current time: {time}
    
    1. {first_instruction}
    2. Reflect and critique your answer. Be severe to maximize improvement.
    3. Recommend search queries to research information and improve your answer.""",
            ),
            MessagesPlaceholder(variable_name="messages"),
            (
                "user",
                "\n\nReflect on the user's original question and the"
                " actions taken thus far. Respond using the {function_name} function.",
            ),
        ]
    ).partial(
        time=lambda: datetime.datetime.now().isoformat(),
    )
    
    initial_answer_chain = actor_prompt_template.partial(
        first_instruction="Provide a detailed ~250 word answer.",
        function_name=AnswerQuestion.__name__,
    ) | llm.bind_tools(tools=[AnswerQuestion])
    # initial_answer_chain = actor_prompt_template.partial(
    #     first_instruction="Provide a detailed ~250 word answer.",
    #     function_name=AnswerQuestion.__name__,
    # ) | llm.with_structured_output(AnswerQuestion)
    
    validator = PydanticToolsParser(tools=[AnswerQuestion])
    
    first_responder = ResponderWithRetries(runnable=initial_answer_chain, validator=validator)
    
    # example_question = "Why is reflection useful in AI?"
    # initial = first_responder.respond([HumanMessage(content=example_question)])
    
    # rich.print(initial)
    
    revise_instructions = """Revise your previous answer using the new information.
        - You should use the previous critique to add important information to your answer.
            - You MUST include numerical citations in your revised answer to ensure it can be verified.
            - Add a "References" section to the bottom of your answer (which does not count towards the word limit). In form of:
                - [1] https://example.com
                - [2] https://example.com
        - You should use the previous critique to remove superfluous information from your answer and make SURE it is not more than 250 words.
    """
    
    revision_chain = actor_prompt_template.partial(
        first_instruction=revise_instructions,
        function_name=ReviseAnswer.__name__,
    ) | llm.bind_tools(tools=[ReviseAnswer])
    # revision_chain = actor_prompt_template.partial(
    #     first_instruction=revise_instructions,
    #     function_name=ReviseAnswer.__name__,
    # ) | llm.with_structured_output(ReviseAnswer)
    
    revision_validator = PydanticToolsParser(tools=[ReviseAnswer])
    
    revisor = ResponderWithRetries(runnable=revision_chain, validator=revision_validator)

    # revised = revisor.respond(
    #     [
    #         HumanMessage(content=example_question),
    #         initial,
    #         ToolMessage(
    #             tool_call_id=initial.tool_calls[0]["id"],
    #             content=json.dumps(
    #                 search_internet.invoke(
    #                     {"query": initial.tool_calls[0]["args"]["search_queries"][0]}
    #                 )
    #             ),
    #         ),
    #     ]
    # )
    # rich.print(revised)
    # print(revised["tool_calls"][0]["args"]["references"])
    
    def run_queries(search_queries: List[str], **kwargs):
        """Run the generated queries."""
        return search_internet.batch([{"query": query} for query in search_queries])
    
    tool_node = ToolNode(
        [
            StructuredTool.from_function(run_queries, name=AnswerQuestion.__name__),
            StructuredTool.from_function(run_queries, name=ReviseAnswer.__name__),
        ]
    )
    
    MAX_ITERATIONS = 3
    
    builder = StateGraph(State)
    
    builder.add_node("draft", first_responder.respond)
    builder.add_node("execute_tools", tool_node)
    builder.add_node("revise", revisor.respond)
    
    builder.add_edge(START, "draft")
    # draft -> execute_tools
    builder.add_edge("draft", "execute_tools")
    # execute_tools -> revise
    builder.add_edge("execute_tools", "revise")
    
    # Define looping logic:
    def _get_num_iterations(messages: List):
        i = 0
        for m in messages[::-1]:
            if m.type not in {"tool", "ai"}:
                break
            i += 1
        return i
    
    def event_loop(state: State) -> Literal["execute_tools", "__end__"]:
        # in our case, we'll just stop after N plans
        messages = state["messages"]
        num_iterations = _get_num_iterations(messages)
        if num_iterations > MAX_ITERATIONS:
            return END
        return "execute_tools"
    
    # revise -> execute_tools OR end
    builder.add_conditional_edges("revise", event_loop)
    
    graph = builder.compile()

    return graph
