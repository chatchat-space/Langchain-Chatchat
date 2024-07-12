"""用于加载reranker模型，封装成api服务
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import time
import uvicorn

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from typing import List,  Optional, Union

from pydantic import BaseModel, Field

from sse_starlette.sse import EventSourceResponse
from FlagEmbedding import FlagReranker
import torch
# Set up limit request time
EventSourceResponse.DEFAULT_PING_INTERVAL = 1000
from chatchat.settings import Settings

reranker_model = FlagReranker(Settings.model_settings.RERANKER_CONFIG['local_path'], 
                              use_fp16=True,
                              device=Settings.model_settings.RERANKER_CONFIG['device']
                              )


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ModelCard(BaseModel):
    id: str
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "owner"
    root: Optional[str] = None
    parent: Optional[str] = None
    permission: Optional[list] = None


class ModelList(BaseModel):
    object: str = "list"
    data: List[ModelCard] = []

class RerankerRequest(BaseModel):
    input: Union[List[str], List[List[str]]]
    model: str = Settings.model_settings.RERANKER_CONFIG['model']

class EmbeddingResponse(BaseModel):
    data: list
    model: str
    object: str
    usage: dict

class RerankerResponse(BaseModel):
    data: list
    model: str
    object: str
    # usage: dict


@app.get("/health")
async def health() -> Response:
    """Health check."""
    return Response(status_code=200)


@app.post("/v1/reranker", response_model=RerankerResponse)
async def rerank_answers(request: RerankerRequest):
    print(request.input)
    scores = reranker_model.compute_score(request.input,batch_size=32)
    if isinstance(scores, float):
        scores = [scores]
    response = {
        "data": [
            {
                "object": "reranker",
                "score": score,
                "index": index
            }
            for index, score in enumerate(scores)
        ],
        "model": request.model,
        "object": "list",
    }
    return response


@app.get("/v1/models", response_model=ModelList)
async def list_models():
    # model_card_emb = ModelCard(
    #     id="text-embedding-ada-002"
    # )
    model_card_rerank = ModelCard(
        id=Settings.model_settings.RERANKER_CONFIG['model']
    )
    return ModelList(
        data=[
            # model_card_emb, 
            model_card_rerank
            ]
    )



if __name__ == "__main__":


    uvicorn.run(app="reranker_api:app", 
                host=Settings.basic_settings.DEFAULT_BIND_HOST, 
                port=Settings.model_settings.RERANKER_CONFIG['port'], 
                workers=Settings.model_settings.RERANKER_CONFIG['num_workers'],
                limit_concurrency=Settings.model_settings.RERANKER_CONFIG["limit_concurrency"],
                )