from langchain.prompts import PromptTemplate
from langchain.chains import LLMMathChain
from server.agent import model_container
from pydantic import BaseModel, Field

_PROMPT_TEMPLATE = """
将数学问题翻译成可以使用Python的numexpr库执行的表达式。使用运行此代码的输出来回答问题。
问题: ${{包含数学问题的问题。}}
```text
${{解决问题的单行数学表达式}}
```
...numexpr.evaluate(query)...
```output
${{运行代码的输出}}
```
答案: ${{答案}}

这是两个例子：

问题: 37593 * 67是多少？
```text
37593 * 67
```
...numexpr.evaluate("37593 * 67")...
```output
2518731

答案: 2518731

问题: 37593的五次方根是多少？
```text
37593**(1/5)
```
...numexpr.evaluate("37593**(1/5)")...
```output
8.222831614237718

答案: 8.222831614237718


问题: 2的平方是多少？
```text
2 ** 2
```
...numexpr.evaluate("2 ** 2")...
```output
4

答案: 4


现在，这是我的问题：
问题: {question}
"""

PROMPT = PromptTemplate(
    input_variables=["question"],
    template=_PROMPT_TEMPLATE,
)


class CalculatorInput(BaseModel):
    query: str = Field()

def calculate(query: str):
    model = model_container.MODEL
    llm_math = LLMMathChain.from_llm(model, verbose=True, prompt=PROMPT)
    ans = llm_math.run(query)
    return ans

if __name__ == "__main__":
    result = calculate("2的三次方")
    print("答案:",result)



