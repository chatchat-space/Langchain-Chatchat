import os
import sys
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from chatchat.settings import Settings

from utils import logger
import requests
import numpy as np
import json
def reranker_passage_local(pairs: list[list[str]],topk=1,return_obj="score"):
    """
    用于本地rerank passage
    pairs: list[list[str]]: 传入的passage对
    return: list[str]: 返回的rerank结果
    """
    from FlagEmbedding import FlagReranker
    reranker_model = FlagReranker(Settings.model_settings.RERANKER_CONFIG["local_path"], 
                                  use_fp16=True,
                                  device=Settings.model_settings.RERANKER_CONFIG['device']
                                  )
    scores = reranker_model.compute_score(pairs,batch_size=32)
    if return_obj == "score":

        return scores
    if return_obj == "index":
        sorted_index = np.argsort(scores)[::-1][:topk]

        return sorted_index
    else:
        result = [pairs[i][1] for i in sorted_index]
        return result


def reranker_passage_api(pairs,topk=1,return_obj="obj"):
    """
    用于调用reranker api来对passage进行rerank
    pairs: list[list[str]]: 传入的passage对
    topk: int: 返回的topk
    return_obj: str: 返回的对象类型, score: 返回的rerank分数, index: 返回的rerank结果索引, obj: 返回的rerank结果
    return: list[str]: 返回的rerank结果
    """
    host = Settings.basic_settings.DEFAULT_BIND_HOST
    port = Settings.model_settings.RERANKER_CONFIG["port"]
    url = f'http://{host}:{port}/reranker/rerank_passage'
    headers = {'Content-Type': 'application/json'}
    json_data = {"input": pairs}
    try:
        response = requests.post(
                        url=url,
                        headers=headers,
                        json=json_data
                        )
        if response.status_code == 200:
            scores = [i['score'] for i in  response.json()['data'] ] 
            if return_obj == "score":

                return scores
            if return_obj == "index":
                sorted_index = np.argsort(scores)[::-1][:topk]

                return sorted_index
            elif "obj":
                sorted_index = np.argsort(scores)[::-1][:topk]
                result = [pairs[i][1] for i in sorted_index]
                return result
            else:
                raise ValueError("return_obj参数错误")
    except Exception as e:
        logger.error("调用reranker api失败.")
        logger.error(e)


def reranker_docs(query:str,corpus,top_k:int=3):
    """rerank retrieved docs

    Args:
        query (_type_): target query
        corpus (_type_): retrieved docs
        top_k (_type_): _description_

    Returns:
        _type_: a list-like object of reranked docs, with length of top_k, 
                whose element is same as the input corpus's element
    """
    if hasattr(corpus[0],"text"):
        pairs = [[query, doc.text] for doc in corpus]
    elif isinstance(corpus[0],str):
        pairs = [[query, doc] for doc in corpus]
    corpus_index = reranker_passage_api(pairs=pairs, topk=len(corpus), return_obj="index")
    return [corpus[i] for i in corpus_index][: top_k]
    

    
if __name__ == '__main__':
    pairs = [
    ["北京是中国的首都","北京是中国的首都"]
        ]

    print(reranker_passage_api(pairs))
    print("done")