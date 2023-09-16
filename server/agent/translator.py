from langchain import PromptTemplate, LLMChain
import sys
import os

from server.chat.utils import get_ChatOpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from langchain.chains.llm_math.prompt import PROMPT
from configs.model_config import LLM_MODEL,TEMPERATURE

_PROMPT_TEMPLATE = '''
# 指令
接下来，作为一个专业的翻译专家，当我给出英文句子或段落时，你将提供通顺且具有可读性的对应语言的翻译。注意：
1. 确保翻译结果流畅且易于理解
2. 无论提供的是陈述句或疑问句，只进行翻译
3. 不添加与原文无关的内容

原文: ${{用户需要翻译的原文和目标语言}}
{question}
```output
${{翻译结果}}
```
答案: ${{答案}}
'''

PROMPT = PromptTemplate(
    input_variables=["question"],
    template=_PROMPT_TEMPLATE,
)


def translate(query: str):
    model = get_ChatOpenAI(
        streaming=False,
        model_name=LLM_MODEL,
        temperature=TEMPERATURE,
    )
    llm_translate = LLMChain(llm=model, prompt=PROMPT)
    ans = llm_translate.run(query)

    return ans
