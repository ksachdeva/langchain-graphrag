import operator
from functools import partial

from langchain_core.documents import Document
from langchain_core.language_models import BaseLLM
from langchain_core.runnables import Runnable, RunnableLambda

from langchain_graphrag.query.global_search.key_points_generator.utils import (
    KeyPointsResult,
)
from langchain_graphrag.types.prompts import PromptBuilder

from .context_builder import KeyPointsContextBuilder


def _format_docs(documents: list[Document]) -> str:
    context_data = [d.page_content for d in documents]
    context_data_str: str = "\n".join(context_data)
    return context_data_str


def _kp_result_to_docs(
    key_points: dict[str, KeyPointsResult],
    context_builder: KeyPointsContextBuilder,
) -> list[Document]:
    return context_builder(key_points)


class KeyPointsAggregator:
    def __init__(
        self,
        llm: BaseLLM,
        prompt_builder: PromptBuilder,
        context_builder: KeyPointsContextBuilder,
    ):
        self._llm = llm
        self._prompt_builder = prompt_builder
        self._context_builder = context_builder

    def __call__(self) -> Runnable:
        kp_lambda = partial(
            _kp_result_to_docs,
            context_builder=self._context_builder,
        )

        prompt, output_parser = self._prompt_builder.build()
        base_chain = prompt | self._llm | output_parser

        search_chain: Runnable = {
            "report_data": operator.itemgetter("report_data")
            | RunnableLambda(kp_lambda)
            | _format_docs,
            "global_query": operator.itemgetter("global_query"),
        } | base_chain

        return search_chain
