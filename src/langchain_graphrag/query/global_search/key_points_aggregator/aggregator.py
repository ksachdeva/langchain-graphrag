from langchain_core.language_models import BaseLLM
from langchain_core.output_parsers.base import BaseOutputParser

from langchain_graphrag.query.global_search.key_points_generator.utils import (
    KeyPointsResult,
)
from langchain_graphrag.types.prompts import PromptBuilder


class KeyPointsAggregator:
    def __init__(
        self,
        prompt_builder: PromptBuilder,
        llm: BaseLLM,
        output_parser: BaseOutputParser,
    ):
        prompt = prompt_builder.build()
        self._chain = prompt | llm | output_parser
        self._prompt_builder = prompt_builder

    def invoke(self, query: str, key_points: list[KeyPointsResult]) -> str:
        chain_input = self._prompt_builder.prepare_chain_input(
            global_query=query,
            key_points=key_points,
        )

        return self._chain.invoke(input=chain_input)
