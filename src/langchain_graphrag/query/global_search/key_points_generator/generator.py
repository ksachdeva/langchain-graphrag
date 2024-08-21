from __future__ import annotations

from langchain_core.documents import Document
from langchain_core.language_models import BaseLLM
from langchain_core.runnables import Runnable, RunnableParallel

from langchain_graphrag.types.prompts import PromptBuilder

from .context_builder import CommunityReportContextBuilder


def _format_docs(documents: list[Document]) -> str:
    context_data = [d.page_content for d in documents]
    context_data_str: str = "\n".join(context_data)
    return context_data_str


def make_key_points_generator_chain(
    llm: BaseLLM,
    prompt_builder: PromptBuilder,
    context_builder: CommunityReportContextBuilder,
) -> Runnable:
    prompt, output_parser = prompt_builder.build()

    documents = context_builder()

    chains: list[Runnable] = []

    for d in documents:
        d_context_data = _format_docs([d])
        d_prompt = prompt.partial(context_data=d_context_data)
        generator_chain: Runnable = d_prompt | llm | output_parser
        chains.append(generator_chain)

    analysts = [f"Analayst-{i}" for i in range(1, len(chains) + 1)]

    return RunnableParallel(dict(zip(analysts, chains, strict=True)))


class KeyPointsGenerator:
    def __init__(
        self,
        llm: BaseLLM,
        prompt_builder: PromptBuilder,
        context_builder: CommunityReportContextBuilder,
    ):
        self._llm = llm
        self._prompt_builder = prompt_builder
        self._context_builder = context_builder

    def __call__(self) -> Runnable:
        return make_key_points_generator_chain(
            llm=self._llm,
            prompt_builder=self._prompt_builder,
            context_builder=self._context_builder,
        )
