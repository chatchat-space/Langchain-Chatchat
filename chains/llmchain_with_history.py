from server.utils import get_ChatOpenAI
from configs.model_config import LLM_MODELS, TEMPERATURE
from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)

model = get_ChatOpenAI(model_name=LLM_MODELS[0], temperature=TEMPERATURE)


human_prompt = "{input}"
human_message_template = HumanMessagePromptTemplate.from_template(human_prompt)

chat_prompt = ChatPromptTemplate.from_messages(
    [("human", "我们来玩成语接龙，我先来，生龙活虎"),
     ("ai", "虎头虎脑"),
     ("human", "{input}")])


chain = LLMChain(prompt=chat_prompt, llm=model, verbose=True)
print(chain({"input": "恼羞成怒"}))