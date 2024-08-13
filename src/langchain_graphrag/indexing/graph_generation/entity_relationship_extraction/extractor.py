import networkx as nx
import pandas as pd
from langchain_core.language_models import BaseLLM
from langchain_core.output_parsers.base import BaseOutputParser
from tqdm import tqdm

from langchain_graphrag.types.prompts import PromptBuilder

from .output_parser import EntityExtractionOutputParser
from .prompt_builder import EntityExtractionPromptBuilder


class EntityRelationshipExtractor:
    def __init__(
        self,
        prompt_builder: PromptBuilder,
        llm: BaseLLM,
        output_parser: BaseOutputParser,
    ):
        prompt = prompt_builder.build()
        self._extraction_chain = prompt | llm | output_parser
        self._prompt_builder = prompt_builder

    @staticmethod
    def build_default(llm: BaseLLM) -> "EntityRelationshipExtractor":
        return EntityRelationshipExtractor(
            prompt_builder=EntityExtractionPromptBuilder(),
            llm=llm,
            output_parser=EntityExtractionOutputParser(),
        )

    def invoke(self, input_data: pd.DataFrame) -> list[nx.Graph]:
        def _run_chain(series: pd.Series) -> nx.Graph:
            _, text_id, text = (
                series["document_id"],
                series["id"],
                series["text"],
            )

            chain_input = self._prompt_builder.prepare_chain_input(text=text)

            chunk_graph = self._extraction_chain.invoke(input=chain_input)

            # add the chunk_id to the nodes
            for node_names in chunk_graph.nodes():
                chunk_graph.nodes[node_names]["text_unit_ids"] = [text_id]

            # add the chunk_id to the edges as well
            for edge_names in chunk_graph.edges():
                chunk_graph.edges[edge_names]["text_unit_ids"] = [text_id]

            return chunk_graph

        tqdm.pandas(desc="Extracting entities and relationships ...")
        chunk_graphs: list[nx.Graph] = input_data.progress_apply(_run_chain, axis=1)

        return chunk_graphs
