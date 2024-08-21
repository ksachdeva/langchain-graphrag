from __future__ import annotations

import networkx as nx
from langchain_core.language_models import BaseLLM

from langchain_graphrag.types.graphs.community import Community
from langchain_graphrag.types.prompts import IndexingPromptBuilder

from .prompt_builder import CommunityReportGenerationPromptBuilder
from .utils import CommunityReportResult


class CommunityReportGenerator:
    def __init__(self, prompt_builder: IndexingPromptBuilder, llm: BaseLLM):
        prompt, output_parser = prompt_builder.build()
        self._chain = prompt | llm | output_parser
        self._prompt_builder = prompt_builder

    @staticmethod
    def build_default(llm: BaseLLM) -> CommunityReportGenerator:
        return CommunityReportGenerator(
            prompt_builder=CommunityReportGenerationPromptBuilder(),
            llm=llm,
        )

    def invoke(self, community: Community, graph: nx.Graph) -> CommunityReportResult:
        chain_input = self._prompt_builder.prepare_chain_input(
            community=community,
            graph=graph,
        )

        return self._chain.invoke(input=chain_input)
