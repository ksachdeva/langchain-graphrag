from typing import Any, Protocol

from langchain_core.prompts import PromptTemplate


class PromptBuilder(Protocol):
    def build(self) -> PromptTemplate: ...

    def prepare_chain_input(self, **kwargs: dict[str, Any]) -> dict[str, str]: ...
