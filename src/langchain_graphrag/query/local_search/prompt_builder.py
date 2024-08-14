from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_core.output_parsers.base import BaseOutputParser
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts import (
    BasePromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)
from typing_extensions import Unpack

from langchain_graphrag.types.prompts import PromptBuilder

from .system_prompt import LOCAL_SEARCH_SYSTEM_PROMPT


class LocalSearchPromptBuilder(PromptBuilder):
    def __init__(
        self,
        *,
        system_prompt: str | None = None,
        system_prompt_path: Path | None = None,
    ):
        self._system_prompt: str | None
        if system_prompt is None and system_prompt_path is None:
            self._system_prompt = LOCAL_SEARCH_SYSTEM_PROMPT
        else:
            self._system_prompt = system_prompt

        self._system_prompt_path = system_prompt_path

    def build(self) -> tuple[BasePromptTemplate, BaseOutputParser]:
        if self._system_prompt:
            system_template = SystemMessagePromptTemplate.from_template(
                self._system_prompt
            )
        else:
            assert self._system_prompt_path is not None
            system_template = SystemMessagePromptTemplate.from_template_file(
                self._system_prompt_path,
                input_variables=["context_data"],
            )

        template = ChatPromptTemplate([system_template, ("user", "{local_query}")])
        output_parser = StrOutputParser()
        return template, output_parser

    def prepare_chain_input(self, **kwargs: Unpack[dict[str, Any]]) -> dict[str, str]:
        local_query: str | None = kwargs.get("local_query", None)
        documents: list[Document] | None = kwargs.get("documents", None)

        if local_query is None:
            raise ValueError("local_query is required")

        if documents is None:
            raise ValueError("documents is required")

        context_data = [d.page_content for d in documents]
        context_data_str: str = "\n".join(context_data)

        return dict(
            response_type="Multiple Paragraphs",
            context_data=context_data_str,
            local_query=local_query,
        )
