from langchain.docstore.document import Document
from configs import EMBEDDING_MODEL, logger, CHUNK_SIZE
from server.utils import BaseResponse, list_embed_models, list_online_embed_models
from fastapi import Body
from fastapi.concurrency import run_in_threadpool
from typing import Dict, List


def embed_texts(
    texts: List[str],
    endpoint_host: str,
    endpoint_host_key: str,
    endpoint_host_proxy: str,
    embed_model: str = EMBEDDING_MODEL,
    to_query: bool = False,
) -> BaseResponse:
    '''
    对文本进行向量化。返回数据格式：BaseResponse(data=List[List[float]])
    TODO: 也许需要加入缓存机制，减少 token 消耗
    '''
    try:
        if embed_model in list_embed_models(): # 使用本地Embeddings模型
            from server.utils import load_local_embeddings
            embeddings = load_local_embeddings(model=embed_model)
            return BaseResponse(data=embeddings.embed_documents(texts))

        # 使用在线API
        if embed_model in list_online_embed_models(endpoint_host=endpoint_host,
                                                   endpoint_host_key=endpoint_host_key,
                                                   endpoint_host_proxy=endpoint_host_proxy):
            from langchain.embeddings.openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings(model=embed_model,
                                          openai_api_key=endpoint_host_key if endpoint_host_key else "None",
                                          openai_api_base=endpoint_host if endpoint_host else "None",
                                          openai_proxy=endpoint_host_proxy if endpoint_host_proxy else None,
                                          chunk_size=CHUNK_SIZE)
            return BaseResponse(data=embeddings.embed_documents(texts))

        return BaseResponse(code=500, msg=f"指定的模型 {embed_model} 不支持 Embeddings 功能。")
    except Exception as e:
        logger.error(e)
        return BaseResponse(code=500, msg=f"文本向量化过程中出现错误：{e}")


async def aembed_texts(
    texts: List[str],
    endpoint_host: str,
    endpoint_host_key: str,
    endpoint_host_proxy: str,
    embed_model: str = EMBEDDING_MODEL,
    to_query: bool = False,
) -> BaseResponse:
    '''
    对文本进行向量化。返回数据格式：BaseResponse(data=List[List[float]])
    '''
    try:
        if embed_model in list_embed_models(): # 使用本地Embeddings模型
            from server.utils import load_local_embeddings

            embeddings = load_local_embeddings(model=embed_model)
            return BaseResponse(data=await embeddings.aembed_documents(texts))

        # 使用在线API
        if embed_model in list_online_embed_models(endpoint_host=endpoint_host,
                                                   endpoint_host_key=endpoint_host_key,
                                                   endpoint_host_proxy=endpoint_host_proxy):
            return await run_in_threadpool(embed_texts,
                                           texts=texts,
                                           endpoint_host=endpoint_host,
                                           endpoint_host_key=endpoint_host_key,
                                           endpoint_host_proxy=endpoint_host_proxy,
                                           embed_model=embed_model,
                                           to_query=to_query)
    except Exception as e:
        logger.error(e)
        return BaseResponse(code=500, msg=f"文本向量化过程中出现错误：{e}")


def embed_texts_endpoint(
    texts: List[str] = Body(..., description="要嵌入的文本列表", examples=[["hello", "world"]]),
    endpoint_host: str = Body(False, description="接入点地址"),
    endpoint_host_key: str = Body(False, description="接入点key"),
    endpoint_host_proxy: str = Body(False, description="接入点代理地址"),
    embed_model: str = Body(EMBEDDING_MODEL, description=f"使用的嵌入模型"),
    to_query: bool = Body(False, description="向量是否用于查询。有些模型如Minimax对存储/查询的向量进行了区分优化。"),
) -> BaseResponse:
    '''
    接入api，对文本进行向量化，返回 BaseResponse(data=List[List[float]])
    '''
    return embed_texts(texts=texts,
                       endpoint_host=endpoint_host,
                       endpoint_host_key=endpoint_host_key,
                       endpoint_host_proxy=endpoint_host_proxy,
                       embed_model=embed_model, to_query=to_query)
