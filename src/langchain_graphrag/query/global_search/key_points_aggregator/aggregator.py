from langchain_core.language_models import BaseLLM
from langchain_core.output_parsers.base import BaseOutputParser
from langchain_core.output_parsers.string import StrOutputParser

from langchain_graphrag.query.global_search.key_points_generator.utils import (
    KeyPointsResult,
)
from langchain_graphrag.types.prompts import PromptBuilder
from .prompt_builder import KeyPointsAggregatorPromptBuilder


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

    @staticmethod
    def build_default(llm: BaseLLM) -> "KeyPointsAggregator":
        return KeyPointsAggregator(
            prompt_builder=KeyPointsAggregatorPromptBuilder(),
            llm=llm,
            output_parser=StrOutputParser(),
        )

    def invoke(self, query: str, key_points: list[KeyPointsResult]) -> str:
        chain_input = self._prompt_builder.prepare_chain_input(
            global_query=query,
            key_points=key_points,
        )

        return self._chain.invoke(input=chain_input)
