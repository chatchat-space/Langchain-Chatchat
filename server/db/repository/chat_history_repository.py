from server.db.session import with_session
from server.db.models.chat_history_model import ChatHistoryModel
import re
import uuid
from typing import Dict, List


def _convert_query(query: str) -> str:
    p = re.sub(r"\s+", "%", query)
    return f"%{p}%"


@with_session
def add_chat_history_to_db(session, chat_type, query, response="", chat_history_id=None, metadata: Dict = {}):
    """
    新增聊天记录
    """
    if not chat_history_id:
        chat_history_id = uuid.uuid4().hex
    ch = ChatHistoryModel(id=chat_history_id, chat_type=chat_type, query=query, response=response,
                        metadata=metadata)
    session.add(ch)
    session.commit()
    return ch.id


@with_session
def update_chat_history(session, chat_history_id, response: str = None, metadata: Dict = None):
    """
    更新已有的聊天记录
    """
    ch = get_chat_history_by_id(chat_history_id)
    if ch is not None:
        if response is not None:
            ch.response = response
        if isinstance(metadata, dict):
            ch.meta_data = metadata
        session.add(ch)
        return ch.id


@with_session
def feedback_chat_history_to_db(session, chat_history_id, feedback_score, feedback_reason):
    """
    反馈聊天记录
    """
    ch = session.query(ChatHistoryModel).filter_by(id=chat_history_id).first()
    if ch:
        ch.feedback_score = feedback_score
        ch.feedback_reason = feedback_reason
        return ch.id


@with_session
def get_chat_history_by_id(session, chat_history_id) -> ChatHistoryModel:
    """
    查询聊天记录
    """
    ch = session.query(ChatHistoryModel).filter_by(id=chat_history_id).first()
    return ch


@with_session
def filter_chat_history(session, query=None, response=None, score=None, reason=None) -> List[ChatHistoryModel]:
    ch =session.query(ChatHistoryModel)
    if query is not None:
        ch = ch.filter(ChatHistoryModel.query.ilike(_convert_query(query)))
    if response is not None:
        ch = ch.filter(ChatHistoryModel.response.ilike(_convert_query(response)))
    if score is not None:
        ch = ch.filter_by(feedback_score=score)
    if reason is not None:
        ch = ch.filter(ChatHistoryModel.feedback_reason.ilike(_convert_query(reason)))

    return ch
