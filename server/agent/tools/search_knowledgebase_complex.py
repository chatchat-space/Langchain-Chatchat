from __future__ import annotations
import json
import re
import warnings
from typing import Dict
from langchain.callbacks.manager import AsyncCallbackManagerForChainRun, CallbackManagerForChainRun
from langchain.chains.llm import LLMChain
from langchain.pydantic_v1 import Extra, root_validator
from langchain.schema import BasePromptTemplate
from langchain.schema.language_model import BaseLanguageModel
from typing import List, Any, Optional
from langchain.prompts import PromptTemplate
from server.chat.knowledge_base_chat import knowledge_base_chat
from configs import VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD, MAX_TOKENS
import asyncio
from server.agent import model_container
from pydantic import BaseModel, Field

async def search_knowledge_base_iter(database: str, query: str) -> str:
    response = await knowledge_base_chat(query=query,
                                         knowledge_base_name=database,
                                         model_name=model_container.MODEL.model_name,
                                         temperature=0.01,
                                         history=[],
                                         top_k=VECTOR_SEARCH_TOP_K,
                                         max_tokens=MAX_TOKENS,
                                         prompt_name="default",
                                         score_threshold=SCORE_THRESHOLD,
                                         stream=False)

    contents = ""
    async for data in response.body_iterator:  # 这里的data是一个json字符串
        data = json.loads(data)
        contents += data["answer"]
        docs = data["docs"]
    return contents


async def search_knowledge_multiple(queries) -> List[str]:
    # queries 应该是一个包含多个 (database, query) 元组的列表
    tasks = [search_knowledge_base_iter(database, query) for database, query in queries]
    results = await asyncio.gather(*tasks)
    # 结合每个查询结果，并在每个查询结果前添加一个自定义的消息
    combined_results = []
    for (database, _), result in zip(queries, results):
        message = f"\n查询到 {database} 知识库的相关信息:\n{result}"
        combined_results.append(message)

    return combined_results


def search_knowledge(queries) -> str:
    responses = asyncio.run(search_knowledge_multiple(queries))
    # 输出每个整合的查询结果
    contents = ""
    for response in responses:
        contents += response + "\n\n"
    return contents


_PROMPT_TEMPLATE = """
用户会提出一个需要你查询知识库的问题，你应该对问题进行理解和拆解，并在知识库中查询相关的内容。

对于每个知识库，你输出的内容应该是一个一行的字符串，这行字符串包含知识库名称和查询内容，中间用逗号隔开，不要有多余的文字和符号。你可以同时查询多个知识库，下面这个例子就是同时查询两个知识库的内容。

例子:

robotic,机器人男女比例是多少
bigdata,大数据的就业情况如何 


这些数据库是你能访问的，冒号之前是他们的名字，冒号之后是他们的功能，你应该参考他们的功能来帮助你思考


{database_names}

你的回答格式应该按照下面的内容，请注意```text 等标记都必须输出，这是我用来提取答案的标记。
不要输出中文的逗号，不要输出引号。

Question: ${{用户的问题}}

```text
${{知识库名称,查询问题,不要带有任何除了,之外的符号,比如不要输出中文的逗号，不要输出引号}}

```output
数据库查询的结果

现在，我们开始作答
问题: {question}
"""

PROMPT = PromptTemplate(
    input_variables=["question", "database_names"],
    template=_PROMPT_TEMPLATE,
)


class LLMKnowledgeChain(LLMChain):
    llm_chain: LLMChain
    llm: Optional[BaseLanguageModel] = None
    """[Deprecated] LLM wrapper to use."""
    prompt: BasePromptTemplate = PROMPT
    """[Deprecated] Prompt to use to translate to python if necessary."""
    database_names: Dict[str, str] = None
    input_key: str = "question"  #: :meta private:
    output_key: str = "answer"  #: :meta private:

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def raise_deprecation(cls, values: Dict) -> Dict:
        if "llm" in values:
            warnings.warn(
                "Directly instantiating an LLMKnowledgeChain with an llm is deprecated. "
                "Please instantiate with llm_chain argument or using the from_llm "
                "class method."
            )
            if "llm_chain" not in values and values["llm"] is not None:
                prompt = values.get("prompt", PROMPT)
                values["llm_chain"] = LLMChain(llm=values["llm"], prompt=prompt)
        return values

    @property
    def input_keys(self) -> List[str]:
        """Expect input key.

        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Expect output key.

        :meta private:
        """
        return [self.output_key]

    def _evaluate_expression(self, queries) -> str:
        try:
            output = search_knowledge(queries)
        except Exception as e:
            output = "输入的信息有误或不存在知识库,错误信息如下:\n"
            return output + str(e)
        return output

    def _process_llm_result(
            self,
            llm_output: str,
            run_manager: CallbackManagerForChainRun
    ) -> Dict[str, str]:

        run_manager.on_text(llm_output, color="green", verbose=self.verbose)

        llm_output = llm_output.strip()
        # text_match = re.search(r"^```text(.*?)```", llm_output, re.DOTALL)
        text_match = re.search(r"```text(.*)", llm_output, re.DOTALL)
        if text_match:
            expression = text_match.group(1).strip()
            cleaned_input_str = (expression.replace("\"", "").replace("“", "").
                                 replace("”", "").replace("```", "").strip())
            lines = cleaned_input_str.split("\n")
            # 使用逗号分割每一行，然后形成一个（数据库，查询）元组的列表

            try:
                queries = [(line.split(",")[0].strip(), line.split(",")[1].strip()) for line in lines]
            except:
                queries = [(line.split("，")[0].strip(), line.split("，")[1].strip()) for line in lines]
            run_manager.on_text("知识库查询询内容:\n\n" + str(queries) + " \n\n", color="blue", verbose=self.verbose)
            output = self._evaluate_expression(queries)
            run_manager.on_text("\nAnswer: ", verbose=self.verbose)
            run_manager.on_text(output, color="yellow", verbose=self.verbose)
            answer = "Answer: " + output
        elif llm_output.startswith("Answer:"):
            answer = llm_output
        elif "Answer:" in llm_output:
            answer = llm_output.split("Answer:")[-1]
        else:
            return {self.output_key: f"输入的格式不对:\n {llm_output}"}
        return {self.output_key: answer}

    async def _aprocess_llm_result(
            self,
            llm_output: str,
            run_manager: AsyncCallbackManagerForChainRun,
    ) -> Dict[str, str]:
        await run_manager.on_text(llm_output, color="green", verbose=self.verbose)
        llm_output = llm_output.strip()
        text_match = re.search(r"```text(.*)", llm_output, re.DOTALL)
        if text_match:

            expression = text_match.group(1).strip()
            cleaned_input_str = (
                expression.replace("\"", "").replace("“", "").replace("”", "").replace("```", "").strip())
            lines = cleaned_input_str.split("\n")
            try:
                queries = [(line.split(",")[0].strip(), line.split(",")[1].strip()) for line in lines]
            except:
                queries = [(line.split("，")[0].strip(), line.split("，")[1].strip()) for line in lines]
            await run_manager.on_text("知识库查询询内容:\n\n" + str(queries) + " \n\n", color="blue",
                                      verbose=self.verbose)

            output = self._evaluate_expression(queries)
            await run_manager.on_text("\nAnswer: ", verbose=self.verbose)
            await run_manager.on_text(output, color="yellow", verbose=self.verbose)
            answer = "Answer: " + output
        elif llm_output.startswith("Answer:"):
            answer = llm_output
        elif "Answer:" in llm_output:
            answer = "Answer: " + llm_output.split("Answer:")[-1]
        else:
            raise ValueError(f"unknown format from LLM: {llm_output}")
        return {self.output_key: answer}

    def _call(
            self,
            inputs: Dict[str, str],
            run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        _run_manager.on_text(inputs[self.input_key])
        self.database_names = model_container.DATABASE
        data_formatted_str = ',\n'.join([f' "{k}":"{v}"' for k, v in self.database_names.items()])
        llm_output = self.llm_chain.predict(
            database_names=data_formatted_str,
            question=inputs[self.input_key],
            stop=["```output"],
            callbacks=_run_manager.get_child(),
        )
        return self._process_llm_result(llm_output, _run_manager)

    async def _acall(
            self,
            inputs: Dict[str, str],
            run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        _run_manager = run_manager or AsyncCallbackManagerForChainRun.get_noop_manager()
        await _run_manager.on_text(inputs[self.input_key])
        self.database_names = model_container.DATABASE
        data_formatted_str = ',\n'.join([f' "{k}":"{v}"' for k, v in self.database_names.items()])
        llm_output = await self.llm_chain.apredict(
            database_names=data_formatted_str,
            question=inputs[self.input_key],
            stop=["```output"],
            callbacks=_run_manager.get_child(),
        )
        return await self._aprocess_llm_result(llm_output, inputs[self.input_key], _run_manager)

    @property
    def _chain_type(self) -> str:
        return "llm_knowledge_chain"

    @classmethod
    def from_llm(
            cls,
            llm: BaseLanguageModel,
            prompt: BasePromptTemplate = PROMPT,
            **kwargs: Any,
    ) -> LLMKnowledgeChain:
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        return cls(llm_chain=llm_chain, **kwargs)


def search_knowledgebase_complex(query: str):
    model = model_container.MODEL
    llm_knowledge = LLMKnowledgeChain.from_llm(model, verbose=True, prompt=PROMPT)
    ans = llm_knowledge.run(query)
    return ans

class KnowledgeSearchInput(BaseModel):
    location: str = Field(description="The query to be searched")

if __name__ == "__main__":
    result = search_knowledgebase_complex("机器人和大数据在代码教学上有什么区别")
    print(result)

# 这是一个正常的切割
#     queries = [
#         ("bigdata", "大数据专业的男女比例"),
#         ("robotic", "机器人专业的优势")
#     ]
#     result = search_knowledge(queries)
#     print(result)
