from __future__ import annotations

from typing import List

from fastapi import APIRouter, Request

from chatchat.server.chat.chat import chat
from chatchat.server.chat.feedback import chat_feedback
from chatchat.server.chat.file_chat import file_chat


chat_router = APIRouter(prefix="/chat", tags=["ChatChat 对话"])

chat_router.post("/chat",
             summary="与llm模型对话(通过LLMChain)",
             )(chat)

chat_router.post("/feedback",
            summary="返回llm模型对话评分",
            )(chat_feedback)

chat_router.post("/file_chat",
            summary="文件对话"
            )(file_chat)