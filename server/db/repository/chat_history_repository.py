from server.db.session import with_session
from typing import Dict
from server.db.models.chat_history_model import ChatHistoryModel


@with_session
def add_chat_history_to_db(session, chat_history_id, chat_type, query, response, metadata: Dict = {}, ):
    """
    新增聊天记录
    """
    ch = ChatHistoryModel(id=chat_history_id, chat_type=chat_type, query=query, response=response,
                          metadata=metadata)
    session.add(ch)


@with_session
def feedback_chat_history_to_db(session, chat_history_id, feedback_score, feedback_reason):
    """
    反馈聊天记录
    """
    ch = session.query(ChatHistoryModel).filter_by(id=chat_history_id).first()
    if ch:
        ch.feedback_score = feedback_score
        ch.feedback_reason = feedback_reason
