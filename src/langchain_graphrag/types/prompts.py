from typing import Any, Protocol
from typing_extensions import Unpack

from langchain_core.prompts import BasePromptTemplate


class PromptBuilder(Protocol):
    def build(self) -> BasePromptTemplate: ...

    def prepare_chain_input(
        self, **kwargs: Unpack[dict[str, Any]]
    ) -> dict[str, str]: ...
