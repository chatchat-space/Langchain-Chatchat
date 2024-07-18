from typing import Optional, List, Literal, Union

from pydantic import Field

from open_chatcaht._constants import MAX_TOKENS, LLM_MODEL, TEMPERATURE, SCORE_THRESHOLD, VECTOR_SEARCH_TOP_K
from open_chatcaht.api_client import ApiClient
from open_chatcaht.types.chat.chat_feedback_param import ChatFeedbackParam
from open_chatcaht.types.chat.chat_message import ChatMessage
from open_chatcaht.types.chat.file_chat_param import FileChatParam
from open_chatcaht.types.chat.kb_chat_param import KbChatParam

API_URI_CHAT_FEEDBACK = "/chat/feedback"
API_URI_FILE_CHAT = "/chat/file_chat"
API_URI_KB_CHAT = "/chat/kb_chat"


class ChatClient(ApiClient):

    def chat_feedback(self,
                      message_id: str,
                      score: int = Field(0, max=100, description="用户评分，满分100，越大表示评价越高"),
                      reason: str = Field("", description="用户评分理由，比如不符合事实等"), ):
        data = ChatFeedbackParam(
            message_id=message_id,
            score=score,
            reason=reason,
        ).dict()
        resp = self._post(API_URI_CHAT_FEEDBACK, data)
        return self._get_response_value(resp)

    def kb_chat(self,
                query: str ,
                mode: Literal["local_kb", "temp_kb", "search_engine"] = "local_kb",
                kb_name: str = "",
                top_k: int = VECTOR_SEARCH_TOP_K,
                score_threshold: float = SCORE_THRESHOLD,
                history: List[Union[ChatMessage, dict]] = [],
                stream: bool = True,
                model: str = LLM_MODEL,
                temperature: float = TEMPERATURE,
                max_tokens: Optional[int] = MAX_TOKENS,
                prompt_name: str = "default",
                return_direct: bool = False,
                ):
        kb_chat_param = KbChatParam(
            query=query,
            mode=mode,
            kb_name=kb_name,
            top_k=top_k,
            score_threshold=score_threshold,
            history=history,
            stream=stream,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_name=prompt_name,
            return_direct=return_direct,
        ).dict()
        response = self._post(API_URI_KB_CHAT, json=kb_chat_param, stream=True)
        return self._httpx_stream2generator(response, as_json=True)

    def file_chat(self,
                  query: str = Field(..., description="用户输入", examples=["你好"]),
                  knowledge_id: str = Field(..., description="临时知识库ID"),
                  top_k: int = Field(VECTOR_SEARCH_TOP_K, description="匹配向量数"),
                  score_threshold: float = Field(
                      SCORE_THRESHOLD,
                      description="知识库匹配相关度阈值，取值范围在0-1之间，SCORE越小，相关度越高，取到1相当于不筛选，建议设置在0.5左右",
                      ge=0,
                      le=2,
                  ),
                  history: List[Union[dict, ChatMessage]] = Field(
                      [],
                      description="历史对话",
                      examples=[
                          [
                              {"role": "user", "content": "我们来玩成语接龙，我先来，生龙活虎"},
                              {"role": "assistant", "content": "虎头虎脑"},
                          ]
                      ],
                  ),
                  stream: bool = Field(False, description="流式输出"),
                  model_name: str = Field(None, description="LLM 模型名称。"),
                  temperature: float = Field(0.01, description="LLM 采样温度", ge=0.0, le=1.0),
                  max_tokens: Optional[int] = Field(
                      None, description="限制LLM生成Token数量，默认None代表模型最大值"
                  ),
                  prompt_name: str = Field(
                      "default",
                      description="使用的prompt模板名称(在 prompt_settings.yaml 中配置)",
                  ),
                  ):
        file_chat_param = FileChatParam(
            query=query,
            knowledge_id=knowledge_id,
            top_k=top_k,
            score_threshold=score_threshold,
            history=history,
            stream=stream,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_name=prompt_name,
        ).dict()
        response = self._post(API_URI_FILE_CHAT, json=file_chat_param, stream=True)
        return self._httpx_stream2generator(response, as_json=True)
