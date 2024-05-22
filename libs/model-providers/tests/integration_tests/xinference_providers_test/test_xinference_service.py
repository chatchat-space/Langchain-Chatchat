import logging

import pytest
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

logger = logging.getLogger(__name__)


@pytest.mark.requires("xinference_client")
def test_llm(init_server: str):
    llm = ChatOpenAI(
        model_name="glm-4",
        openai_api_key="YOUR_API_KEY",
        openai_api_base=f"{init_server}/xinference/v1",
    )
    template = """Question: {question}
    
    Answer: Let's think step by step."""

    prompt = PromptTemplate.from_template(template)

    llm_chain = LLMChain(prompt=prompt, llm=llm)
    responses = llm_chain.run("你好")
    logger.info("\033[1;32m" + f"llm_chain: {responses}" + "\033[0m")


@pytest.mark.requires("xinference-client")
def test_embedding(init_server: str):
    embeddings = OpenAIEmbeddings(
        model="text_embedding",
        openai_api_key="YOUR_API_KEY",
        openai_api_base=f"{init_server}/xinference/v1",
    )

    text = "你好"

    query_result = embeddings.embed_query(text)

    logger.info("\033[1;32m" + f"embeddings: {query_result}" + "\033[0m")
