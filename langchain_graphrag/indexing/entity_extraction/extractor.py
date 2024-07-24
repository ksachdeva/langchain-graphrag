import pandas as pd
import networkx as nx

from tqdm import tqdm

from langchain_core.language_models import BaseLLM
from langchain_core.output_parsers.base import BaseOutputParser

from .prompt import EntityExtractionPromptBuilder


class EntityRelationshipExtractor:
    def __init__(
        self,
        prompt_builder: EntityExtractionPromptBuilder,
        llm: BaseLLM,
        output_parser: BaseOutputParser,
    ):
        prompt = prompt_builder.build()
        self._extraction_chain = prompt | llm | output_parser

    def _process_dataframe(self, df: pd.DataFrame) -> nx.Graph:
        def run_chain(series: pd.Series) -> nx.Graph:
            document_id, chunk_id, chunk_text = (
                series["document_id"],
                series["chunk_id"],
                series["chunk"],
            )
            graph_row = self._extraction_chain.invoke(input=dict(input_text=chunk_text))
            print(graph_row)
            return graph_row

        tqdm.pandas(desc="Extracting entities and relationships ...")
        df.head(10).progress_apply(run_chain, axis=1)

        graph = nx.Graph()
        # for entity in all_entities:
        #     graph.add_node(entity)

        return graph

    def invoke(self, input_data: str | pd.DataFrame) -> nx.Graph:
        if isinstance(input_data, pd.DataFrame):
            return self._process_dataframe(input_data)
        return self._extraction_chain.invoke(input=dict(input_text=input_data))
