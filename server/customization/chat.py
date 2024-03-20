import codecs
import csv
from collections import defaultdict

from configs import logger
from typing import Optional
from urllib.parse import urlencode

from fastapi import UploadFile, File, Body, Request
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate

from configs import VECTOR_SEARCH_TOP_K, SCORE_THRESHOLD, LLM_MODELS, TEMPERATURE
from server.chat.utils import History
from server.knowledge_base.kb_doc_api import search_docs
from server.knowledge_base.kb_service.base import KBServiceFactory
from server.utils import BaseResponse, get_ChatOpenAI, get_prompt_template, wrap_done, ListResponse


QUERY_TEMPLATE = '当前字段的名称是：{column_name},字段取值是：{column_value}，告诉我其对应的标准字段名称和可能的取值，并通过如下格式返回结果\n' \
                 '标准字段名称:标准字段取值'


def kb_chat_with_csv_file(
        file: UploadFile = File(..., description="上传csv原始数据文件"),
        knowledge_base_name: str = Body(..., description="知识库名称", examples=["samples"]),
        top_k: int = Body(VECTOR_SEARCH_TOP_K, description="匹配向量数"),
        score_threshold: float = Body(SCORE_THRESHOLD,
                                      description="知识库匹配相关度阈值，取值范围在0-1之间，"
                                                  "SCORE越小，相关度越高，"
                                                  "取到1相当于不筛选，建议设置在0.5左右",
                                      ge=0, le=1),
        model_name: str = Body(LLM_MODELS[0], description="用于问答的LLM 模型名称。"),
        temperature: float = Body(TEMPERATURE, description="LLM 采样温度", ge=0.0, le=1.0),
        max_tokens: Optional[int] = Body(
            None,
            description="限制LLM生成Token数量，默认None代表模型最大值"
        ),
        prompt_name: str = Body(
            "default",
            description="使用的prompt模板名称(在configs/prompt_config.py中配置)"
        ),
        request: Request = None,
) -> BaseResponse:
    """
    上传原始数据文件后，使用指定知识库作为Context，进行相似度匹配后执行问答
    """
    kb = KBServiceFactory.get_service_by_name(knowledge_base_name)
    if kb is None:
        logger.error(f'Can not find {knowledge_base_name}!')
        # return BaseResponse(code=404, msg=f"未找到知识库 {knowledge_base_name}", data=[None])

    # Construct queries from CSV file
    input_data_dict = read_file(file)
    logger.info(f'Input data: {input_data_dict}')

    # Call knowledge base chat one by one to get the answer
    responses = []
    for col_name, col_val in input_data_dict.items():
        col_val_list = list(col_val)
        query = QUERY_TEMPLATE.format(column_name=col_name, column_value=col_val_list[0])
        result = knowledge_base_chat_iterator_mockup(
            knowledge_base_name,
            score_threshold,
            query,
            top_k,
            max_tokens,
            model_name,
            prompt_name,
            temperature,
            request
        )
        responses.append(
            {
                'src_col_name': col_name,
                'src_col_val': col_val_list,
                'result': result
            }
        )
    logger.info(f'Final data: {responses}')
    return BaseResponse(data=responses)


def read_file(file):
    """
    Read csv file and conver to dict as below:
    col_a: {va1, va2, va3, ...}
    col_b: {vb1, vb2, vb3, ...}
    ...: ...
    """
    csv_reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
    data = defaultdict(set)
    for row in csv_reader:
        logger.info(f'{row}')
        for k, v in row.items():
            data[k].add(v)
    file.file.close()
    return data


def knowledge_base_chat_iterator(
        knowledge_base_name: str,
        score_threshold: float,
        query: str,
        top_k: int,
        max_tokens: Optional[int],
        model_name: str,
        prompt_name: str,
        temperature: float,
        request: Request,
):
    """
    知识库问答，返回JSON格式的结果
    {
      'answer': "xxxx",
      'docs': [source_doc, ...]
    }
    """
    # Load LLM
    model = get_ChatOpenAI(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Knowledge Base Search
    docs = search_docs(query=query,
                       knowledge_base_name=knowledge_base_name,
                       top_k=top_k,
                       score_threshold=score_threshold)
    context = "\n".join([doc.page_content for doc in docs])

    # Compose prompt based on searching results
    if len(docs) == 0:  # 如果没有找到相关文档，使用empty模板
        prompt_template = get_prompt_template("knowledge_base_chat", "empty")
    else:
        prompt_template = get_prompt_template("knowledge_base_chat", prompt_name)
    input_msg = History(role="user", content=prompt_template).to_msg_template(False)
    chat_prompt = ChatPromptTemplate.from_messages([input_msg])

    # Execute LLMChain directly
    answer = LLMChain(prompt=chat_prompt, llm=model).invoke({"context": context, "question": query})

    # Add original search results into the final answers
    source_documents = []
    for inum, doc in enumerate(docs):
        filename = doc.metadata.get("source")
        parameters = urlencode({"knowledge_base_name": knowledge_base_name, "file_name": filename})
        base_url = request.base_url
        url = f"{base_url}knowledge_base/download_doc?" + parameters
        text = f"""出处 [{inum + 1}] [{filename}]({url}) \n\n{doc.page_content}\n\n"""
        source_documents.append(text)

    if len(source_documents) == 0:  # 没有找到相关文档
        source_documents.append(f"<span style='color:red'>未找到相关文档,该回答为大模型自身能力解答！</span>")

    return {
        "answer": answer,
        "docs": source_documents
    }


def knowledge_base_chat_iterator_mockup(
        knowledge_base_name: str,
        score_threshold: float,
        query: str,
        top_k: int,
        max_tokens: Optional[int],
        model_name: str,
        prompt_name: str,
        temperature: float,
        request: Request,
):
    logger.info(f'{knowledge_base_name}\n{score_threshold}\n{query}\n{top_k}\n{max_tokens}\n{model_name}\n{prompt_name}'
                f'\n{temperature}\n{request}')
    return {
        "answer": "no correct answer",
        "docs": []
    }
