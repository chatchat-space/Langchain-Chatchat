# -*- coding: utf-8 -*-
from langchain_chatchat.utils.history import History
import pydantic
PYDANTIC_V2 = pydantic.VERSION.startswith("2.")

__all__ = ["History", "PYDANTIC_V2"]