from typing import Dict, Any
from .nodes_registry import regist_nodes
from chatchat.server.utils import get_ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from chatchat.server.knowledge_base.kb_doc_api import search_docs
from langchain.prompts.prompt import PromptTemplate
from chatchat.server.utils import (
    get_prompt_template,
)
@regist_nodes(title="KNOWLEGE", description="知识库")
def knowlege(*args: Any, **kwargs) -> Dict[str, Any]:
    model_name = kwargs.get("model", "")
    question = kwargs.get("question", "")
    knowledge_base = kwargs.get("knowledge_base", "")
    top_k = kwargs.get("top_k", 3)
    # top_k转为整数
    top_k = int(top_k)
    score_threshold = kwargs.get("score_threshold", 0.5)        
    docs = search_docs(
        query=question,
        knowledge_base_name=knowledge_base,
        top_k=top_k,
        score_threshold=score_threshold,
        file_name="",
        metadata={},
    )

    llm = get_ChatOpenAI(
        model_name=model_name,
        temperature=0.1,
        streaming=False,
        local_wrap=False,
        verbose=True,
    )
    prompt_template = PromptTemplate.from_template(
                get_prompt_template("llm_model", "rag"), template_format="jinja2"
            )
    rag_chain = prompt_template | llm | StrOutputParser()
    # RAG generation
    generation = rag_chain.invoke({"context": docs, "question": question})
    return {"result":generation}
