from typing import List, Optional
from server.knowledge_base.model.kb_document_model import DocumentWithVSId
from configs.model_config import logger
import sys
import asyncio


# TODO 暂不考虑文件更新，需要重新删除相关文档，再重新添加
class SummaryAdapter:

    _OVERLAP_SIZE: int
    _separator: str = "\n\n"

    def __init__(self, overlap_size: int):
        self._OVERLAP_SIZE = overlap_size

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
        merge_docs = self._drop_overlap(docs)
        print(merge_docs)

    def _drop_overlap(self, docs: List[DocumentWithVSId]) -> List[str]:
        """
         # 将文档中page_content句子叠加的部分去掉
        :param docs:
        :param separator:
        :return:
        """
        merge_docs = []

        pre_doc = None
        for doc in docs:
            # 第一个文档直接添加
            if len(merge_docs) == 0:
                pre_doc = doc.page_content
                merge_docs.append(doc.page_content)
                continue

            # 列表中上一个结尾与下一个开头重叠的部分，删除下一个开头重叠的部分
            # 迭代递减pre_doc的长度，每次迭代删除前面的字符，
            # 查询重叠部分，直到pre_doc的长度小于 self._OVERLAP_SIZE // 2 - 2len(separator)
            for i in range(len(pre_doc), self._OVERLAP_SIZE // 2 - 2 * len(self._separator), -1):
                # 每次迭代删除前面的字符
                pre_doc = pre_doc[1:]
                if doc.page_content[:len(pre_doc)] == pre_doc:
                    # 删除下一个开头重叠的部分
                    merge_docs.append(doc.page_content[len(pre_doc):])
                    break

            pre_doc = doc.page_content

        return merge_docs

    def _join_docs(self, docs: List[str]) -> Optional[str]:
        text = separator.join(docs)
        text = text.strip()
        if text == "":
            return None
        else:
            return text

    def clear_kb_summary(self,
                         kb_name: str):
        pass


if __name__ == '__main__':

    docs = [

        '梦者有特别的作用，也就是说梦是在预卜未来。因此，梦内容的',

        '梦内容的多彩多姿以及对梦者本身所遗留的特殊印象，使他们很难想象',

        '使他们很难想象出一套系统划一的观念，而需要以其个别的价值与可靠性作各',
        '值与可靠性作各种不同的分化与聚合。因此，古代哲学家们对梦的评价也就完全'
    ]
    _OVERLAP_SIZE = 1
    separator: str = "\n\n"
    merge_docs = []
    # 将文档中page_content句子叠加的部分去掉，
    # 列表中上一个结尾与下一个开头重叠的部分，删除下一个开头重叠的部分
    pre_doc = None
    for doc in docs:
        # 第一个文档直接添加
        if len(merge_docs) == 0:

            pre_doc = doc
            merge_docs.append(doc)
            continue

        # 列表中上一个结尾与下一个开头重叠的部分，删除下一个开头重叠的部分
        # 迭代递减pre_doc的长度，每次迭代删除前面的字符，
        # 查询重叠部分，直到pre_doc的长度小于 _OVERLAP_SIZE-2len(separator)
        for i in range(len(pre_doc), _OVERLAP_SIZE - 2 * len(separator), -1):
            # 每次迭代删除前面的字符
            pre_doc = pre_doc[1:]
            if doc[:len(pre_doc)] == pre_doc:
                # 删除下一个开头重叠的部分
                page_content = doc[len(pre_doc):]
                merge_docs.append(page_content)

                pre_doc = doc
                break



    # 将merge_docs中的句子合并成一个文档
    text = separator.join(merge_docs)
    text = text.strip()

    print(text)
