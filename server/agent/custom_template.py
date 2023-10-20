from __future__ import annotations
from langchain.agents import Tool, AgentOutputParser
from langchain.prompts import StringPromptTemplate
from typing import List
from langchain.schema import AgentAction, AgentFinish
from server.agent import model_container
class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
            # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        # Return the formatted templatepr
        # print( self.template.format(**kwargs), end="\n\n")
        return self.template.format(**kwargs)


class CustomOutputParser(AgentOutputParser):
    begin: bool = False
    def __init__(self):
        super().__init__()
        self.begin = True

    def parse(self, llm_output: str) -> AgentFinish | tuple[dict[str, str], str] | AgentAction:
        # Check if agent should finish
        support_agent = ["Azure-OpenAI", "OpenAI", "Anthropic", "Qwen", "qwen-api", "baichuan-api"]  # 目前支持agent的模型
        if not any(agent in model_container.MODEL for agent in support_agent) and self.begin:
            self.begin = False
            stop_words = ["Observation:"]
            min_index = len(llm_output)
            for stop_word in stop_words:
                index = llm_output.find(stop_word)
                if index != -1 and index < min_index:
                    min_index = index
                llm_output = llm_output[:min_index]

        if "Final Answer:" in llm_output:
            self.begin = True
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:", 1)[-1].strip()},
                log=llm_output,
            )

        # Parse out the action and action input
        parts = llm_output.split("Action:")
        if len(parts) < 2:
            return AgentFinish(
                return_values={"output": f"调用agent失败: `{llm_output}`"},
                log=llm_output,
            )

        action = parts[1].split("Action Input:")[0].strip()
        action_input = parts[1].split("Action Input:")[1].strip()

        # 原来的正则化检查方式
        # regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        # print("llm_output",llm_output)
        # match = re.search(regex, llm_output, re.DOTALL)
        # print("match",match)
        # if not match:
        #     return AgentFinish(
        #         return_values={"output": f"调用agent失败: `{llm_output}`"},
        #         log=llm_output,
        #     )
        # action = match.group(1).strip()
        # action_input = match.group(2)

        # Return the action and action input

        try:
            ans = AgentAction(
                tool=action,
                tool_input=action_input.strip(" ").strip('"'),
                log=llm_output
            )
            return ans
        except:
            return AgentFinish(
                return_values={"output": f"调用agent失败: `{llm_output}`"},
                log=llm_output,
            )
