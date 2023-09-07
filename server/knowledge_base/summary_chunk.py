from typing import List
from server.knowledge_base.model.kb_document_model import DocumentWithVSId
from configs.model_config import logger
import sys
import asyncio


# TODO 暂不考虑文件更新，需要重新删除相关文档，再重新添加
class SummaryAdapter:

    def summarize(self,
                  kb_name: str,
                  file_description: str,
                  docs: List[DocumentWithVSId] = []
                  ):

        if sys.version_info < (3, 10):
            loop = asyncio.get_event_loop()
        else:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()

            asyncio.set_event_loop(loop)
        # 同步调用协程代码
        loop.run_until_complete(self.asummarize(kb_name=kb_name,
                                                file_description=file_description,
                                                docs=docs))

    async def asummarize(self,
                         kb_name: str,
                         file_description: str,
                         docs: List[DocumentWithVSId] = []):

        logger.info("start summary")

    def clear_kb_summary(self,
                         kb_name: str):
        pass
