from fastapi import Body
from configs import logger, log_verbose
from server.utils import BaseResponse
from server.db.repository.chat_history_repository import feedback_chat_history_to_db


async def feedback(chat_history_id: str = Body("", max_length=20, description="聊天记录id"),
                   feedback_score: int = Body(None, max=100, description="用户评分，满分100，越大表示评价越高"),
                   feedback_reason: str = Body("",
                                               description="用户评分理由，比如不符合事实等")
                   ):
    try:
        feedback_chat_history_to_db(chat_history_id, feedback_score, feedback_reason)
    except Exception as e:
        msg = f"反馈聊天记录出错： {e}"
        logger.error(f'{e.__class__.__name__}: {msg}',
                     exc_info=e if log_verbose else None)
        return BaseResponse(code=500, msg=msg)

    return BaseResponse(code=200, msg=f"已反馈聊天记录 {chat_history_id}")
