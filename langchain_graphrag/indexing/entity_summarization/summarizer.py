from typing import Optional

from tqdm import tqdm

import networkx as nx

from langchain_core.language_models import BaseLLM
from langchain_core.output_parsers.base import BaseOutputParser

from langchain_graphrag.protocols import PromptBuilder


class EntityRelationshipDescriptionSummarizer:
    def __init__(
        self,
        prompt_builder: PromptBuilder,
        llm: BaseLLM,
        output_parser: Optional[BaseOutputParser] = None,
    ):
        prompt = prompt_builder.build()
        self._summarize_chain = prompt | llm
        if output_parser:
            self._summarize_chain = self._summarize_chain | output_parser

    def invoke(self, graph: nx.Graph) -> nx.Graph:
        for node_name, node in tqdm(
            graph.nodes(data=True), desc="Summarizing entities descriptions"
        ):
            if len(node["description"]) == 1:
                node["description"] = node["description"][0]
                continue

            node["description"] = self._summarize_chain.invoke(
                input=dict(description_list=node["description"], entity_name=node_name)
            )

        for from_node, to_node, edge in tqdm(
            graph.edges(data=True), desc="Summarizing relationship descriptions"
        ):
            if len(edge["description"]) == 1:
                edge["description"] = edge["description"][0]
                continue

            edge["description"] = self._summarize_chain.invoke(
                input=dict(
                    description_list=edge["description"],
                    entity_name=f"{from_node} -> {to_node}",
                )
            )

        return graph
