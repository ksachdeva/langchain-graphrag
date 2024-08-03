from typing import Protocol

from langchain_core.prompts import PromptTemplate


class PromptBuilder(Protocol):
    def build(self) -> PromptTemplate:
        pass
