from langchain_core.language_models import BaseLLM
from langchain_core.output_parsers.base import BaseOutputParser

from langchain_graphrag.query.global_search.community_report import CommunityReport
from langchain_graphrag.types.prompts import PromptBuilder

from .utils import KeyPointsResult
from .prompt_builder import KeyPointsGeneratorPromptBuilder
from .output_parser import KeyPointsOutputParser


class KeyPointsGenerator:
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
    def build_default(llm: BaseLLM) -> "KeyPointsGenerator":
        return KeyPointsGenerator(
            prompt_builder=KeyPointsGeneratorPromptBuilder(),
            llm=llm,
            output_parser=KeyPointsOutputParser(),
        )

    def invoke(self, query: str, reports: list[CommunityReport]) -> KeyPointsResult:
        chain_input = self._prompt_builder.prepare_chain_input(
            global_query=query,
            reports=reports,
        )

        return self._chain.invoke(input=chain_input)
