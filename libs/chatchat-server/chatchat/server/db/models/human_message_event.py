from sqlalchemy import JSON, Column, DateTime, Integer, String, func

from chatchat.server.db.base import Base


class HumanMessageEvent(Base):
    """
    人类反馈消息事件模型
    """

    __tablename__ = "human_message_event"
    call_id = Column(String(32), primary_key=True, comment="聊天记录ID")
    conversation_id = Column(String(32), default=None, index=True, comment="对话框ID")
    function_name = Column(String(50), comment="Function Name")
    kwargs = Column(String(4096), comment="parameters")
    requested = Column(DateTime, default=func.now(), comment="请求时间")
    comment = Column(String(4096), comment="用户评价")
    action = Column(String(50), comment="用户行为")

    def __repr__(self):
        return (f"<human_message_event(id='{self.call_id}', conversation_id='{self.conversation_id}', "
                f"function_name='{self.function_name}', kwargs='{self.kwargs}', "
                f"requested='{self.requested}', comment='{self.comment}', action='{self.action}')>")