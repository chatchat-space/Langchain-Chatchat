import uuid
from typing import Dict, List

from chatchat.server.db.models.human_message_event import HumanMessageEvent
from chatchat.server.db.session import with_session


@with_session
def add_human_message_event_to_db(
        session,
        call_id: str,
        conversation_id: str,
        function_name: str,
        kwargs: str,
        comment: str,
        action: str,
):
    """
    新增人类反馈消息事件
    """
    m = HumanMessageEvent(
        call_id=call_id,
        conversation_id=conversation_id,
        function_name=function_name,
        kwargs=kwargs,
        comment=comment,
        action=action,
    )
    session.add(m)
    session.commit()
    return m.id


@with_session
def get_human_message_event_by_id(session, call_id) -> HumanMessageEvent:
    """
    查询人类反馈消息事件
    """
    m = session.query(HumanMessageEvent).filter_by(call_id=call_id).first()
    return m


@with_session
def list_human_message_event(session, conversation_id: str) -> List[HumanMessageEvent]:
    """
    查询人类反馈消息事件
    """
    m = session.query(HumanMessageEvent).filter_by(conversation_id=conversation_id).all()
    return m


@with_session
def update_human_message_event(session, call_id, comment: str = None, action: str = None):
    """
    更新已有的人类反馈消息事件
    """
    m = get_human_message_event_by_id(call_id)
    if m is not None:
        if comment is not None:
            m.comment = comment
        if action is not None:
            m.action = action
        session.add(m)
        session.commit()
        return m.id
