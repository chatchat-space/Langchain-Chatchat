from fastapi import Body

from chatchat.utils import build_logger
from chatchat.server.db.repository import get_human_message_event_by_id, update_human_message_event, \
    add_human_message_event_to_db, list_human_message_event
from chatchat.server.utils import BaseResponse

logger = build_logger()


def function_calls(
    call_id: str = Body("", description="call_id"),
    conversation_id: str = Body("", description="对话框ID"),
    function_name: str = Body("", description="Function Name"),
    kwargs: str = Body("", description="parameters"),
    comment: str = Body("", description="用户评价"),
    action: str = Body("", description="用户行为")
):
    """
    新增人类反馈消息事件
    """
    try:
        add_human_message_event_to_db(call_id,conversation_id, function_name, kwargs,comment, action)
    except Exception as e:
        msg = f"新增人类反馈消息事件出错： {e}"
        logger.error(f"{e.__class__.__name__}: {msg}")
        return BaseResponse(code=500, msg=msg)
    return BaseResponse(code=200, msg=f"已反馈聊天记录 {call_id}", data={"call_id": call_id})


def get_function_call(call_id: str):
    """
    查询人类反馈消息事件
    """
    try:
        return get_human_message_event_by_id(call_id)
    except Exception as e:
        msg = f"��询人类反馈消息事件出错： {e}"
        logger.error(f"{e.__class__.__name__}: {msg}")
        return BaseResponse(code=500, msg=msg)


def respond_function_call(call_id: str, comment: str, action: str):
    """
    更新已有的人类反馈消息事件
    """
    try:
        update_human_message_event(call_id, comment, action)
    except Exception as e:
        msg = f"更新已有的人类反馈消息事件出错： {e}"
        logger.error(f"{e.__class__.__name__}: {msg}")
        return BaseResponse(code=500, msg=msg)
    return BaseResponse(code=200, msg=f"已更新聊天记录 {call_id}")