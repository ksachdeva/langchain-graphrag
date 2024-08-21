from pathlib import Path

from langchain_core.output_parsers.base import BaseOutputParser
from langchain_core.prompts import (
    BasePromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)

from langchain_graphrag.types.prompts import PromptBuilder

from ._output_parser import KeyPointsOutputParser
from ._system_prompt import MAP_SYSTEM_PROMPT


class KeyPointsGeneratorPromptBuilder(PromptBuilder):
    def __init__(
        self,
        *,
        system_prompt: str | None = None,
        system_prompt_path: Path | None = None,
    ):
        self._system_prompt: str | None
        if system_prompt is None and system_prompt_path is None:
            self._system_prompt = MAP_SYSTEM_PROMPT
        else:
            self._system_prompt = system_prompt

        self._system_prompt_path = system_prompt_path

    def build(self) -> tuple[BasePromptTemplate, BaseOutputParser]:
        if self._system_prompt_path:
            prompt = Path.read_text(self._system_prompt_path)
        else:
            assert self._system_prompt is not None
            prompt = self._system_prompt

        system_template = SystemMessagePromptTemplate.from_template(prompt)

        template = ChatPromptTemplate([system_template, ("user", "{global_query}")])
        return template, KeyPointsOutputParser()
