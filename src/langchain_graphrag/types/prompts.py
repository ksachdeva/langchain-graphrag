from typing import Any, Protocol
from typing import Unpack

from langchain_core.prompts import PromptTemplate


class PromptBuilder(Protocol):
    def build(self) -> PromptTemplate: ...

    def prepare_chain_input(
        self, **kwargs: Unpack[dict[str, Any]]
    ) -> dict[str, str]: ...
