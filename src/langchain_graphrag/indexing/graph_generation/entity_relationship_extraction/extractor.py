from random import Random

import networkx as nx
import pandas as pd
from langchain_core.language_models import BaseLLM
from langchain_core.output_parsers.base import BaseOutputParser
from tqdm import tqdm

from langchain_graphrag.types.prompts import PromptBuilder
from langchain_graphrag.utils.uuid import gen_uuid

from .graphs_merger import GraphsMerger


class EntityRelationshipExtractor:
    def __init__(
        self,
        prompt_builder: PromptBuilder,
        llm: BaseLLM,
        output_parser: BaseOutputParser,
        graphs_merger: GraphsMerger,
        seed: int = 0xF001,
    ):
        prompt = prompt_builder.build()
        self._graphs_merger = graphs_merger
        self._extraction_chain = prompt | llm | output_parser
        self._seed = seed

    def invoke(self, input_data: pd.DataFrame) -> nx.Graph:
        def _run_chain(series: pd.Series) -> nx.Graph:
            _, text_id, text = (
                series["document_id"],
                series["id"],
                series["text"],
            )
            chunk_graph = self._extraction_chain.invoke(input=dict(input_text=text))

            # add the chunk_id to the nodes
            for node_names in chunk_graph.nodes():
                chunk_graph.nodes[node_names]["text_unit_ids"] = [text_id]

            # add the chunk_id to the edges as well
            for edge_names in chunk_graph.edges():
                chunk_graph.edges[edge_names]["text_unit_ids"] = [text_id]

            return chunk_graph

        tqdm.pandas(desc="Extracting entities and relationships ...")
        chunk_graphs: list[nx.Graph] = input_data.progress_apply(_run_chain, axis=1)

        # Merge the graphs per text unit
        graph = self._graphs_merger(chunk_graphs)

        # add degree as an attribute
        for node_degree in graph.degree:
            graph.nodes[str(node_degree[0])]["degree"] = int(node_degree[1])

        # add source degree, target degree and rank as attributes
        # to the edges
        for source, target in graph.edges():
            source_degree = graph.nodes[source]["degree"]
            target_degree = graph.nodes[target]["degree"]
            graph.edges[source, target]["source_degree"] = source_degree
            graph.edges[source, target]["target_degree"] = target_degree
            graph.edges[source, target]["rank"] = source_degree + target_degree

        random = Random(self._seed)  # noqa: S311

        # add ids to nodes
        for index, node in enumerate(graph.nodes()):
            graph.nodes[node]["human_readable_id"] = index
            graph.nodes[node]["id"] = str(gen_uuid(random))

        # add ids to edges
        for index, edge in enumerate(graph.edges()):
            graph.edges[edge]["human_readable_id"] = index
            graph.edges[edge]["id"] = str(gen_uuid(random))

        return graph
