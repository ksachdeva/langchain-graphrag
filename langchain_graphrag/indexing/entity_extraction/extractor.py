import pandas as pd
import networkx as nx

from tqdm import tqdm

from langchain_core.language_models import BaseLLM
from langchain_core.output_parsers.base import BaseOutputParser

from langchain_graphrag.protocols import PromptBuilder

from .graphs_merger import GraphsMerger


class EntityRelationshipExtractor:
    def __init__(
        self,
        prompt_builder: PromptBuilder,
        llm: BaseLLM,
        output_parser: BaseOutputParser,
        graphs_merger: GraphsMerger,
    ):
        prompt = prompt_builder.build()
        self._graphs_merger = graphs_merger
        self._extraction_chain = prompt | llm | output_parser

    def _process_dataframe(self, df: pd.DataFrame) -> tuple[nx.Graph]:
        def _run_chain(series: pd.Series) -> nx.Graph:
            document_id, chunk_id, chunk_text = (
                series["document_id"],
                series["chunk_id"],
                series["chunk"],
            )
            graph = self._extraction_chain.invoke(input=dict(input_text=chunk_text))

            # add the chunk_id to the nodes
            for node_names in graph.nodes():
                graph.nodes[node_names]["source_id"] = [chunk_id]

            # add the chunk_id to the edges as well
            for edge_names in graph.edges():
                graph.edges[edge_names]["source_id"] = [chunk_id]

            return graph

        tqdm.pandas(desc="Extracting entities and relationships ...")
        graphs: list[nx.Graph] = df.progress_apply(_run_chain, axis=1)

        return self._graphs_merger(graphs)

    def invoke(self, input_data: str | pd.DataFrame) -> nx.Graph:
        if isinstance(input_data, pd.DataFrame):
            return self._process_dataframe(input_data)
        return self._extraction_chain.invoke(input=dict(input_text=input_data))
