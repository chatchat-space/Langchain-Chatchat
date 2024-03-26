from typing import List, Optional, Any
from langchain.text_splitter import TextSplitter

class QATextSplitter(TextSplitter):
    """Splitting QA file. Temporary only support json file."""
    def __init__(
        self,
        keep_separator: bool = True,
        **kwargs: Any,
    ) -> None:
        """Create a new TextSplitter."""
        super().__init__(keep_separator=keep_separator, **kwargs)


    def split_text(self, text: str) -> List[str]:
        json_text = eval(text)

        splits = []
        for qa in json_text:
            question = qa["问题"]
            answer = qa["答案"]
        
            splits.append(f"问题：{question}\n答案：{answer}")

        return splits