from copy import deepcopy

import networkx as nx
import pandas as pd

from .entity_relationship_extraction import EntityRelationshipExtractor
from .entity_relationship_summarization import EntityRelationshipDescriptionSummarizer
from .graphs_merger import GraphsMerger


class GraphGenerator:
    def __init__(
        self,
        er_extractor: EntityRelationshipExtractor,
        graphs_merger: GraphsMerger,
        er_description_summarizer: EntityRelationshipDescriptionSummarizer,
    ):
        self._er_extractor = er_extractor
        self._graphs_merger = graphs_merger
        self._er_description_summarizer = er_description_summarizer

    def run(self, text_units: pd.DataFrame) -> tuple[nx.Graph, nx.Graph]:
        er_graphs = self._er_extractor.invoke(text_units)
        er_merged_graph = self._graphs_merger(er_graphs)
        er_summarized_graph = self._er_description_summarizer.invoke(
            deepcopy(er_merged_graph)
        )
        return er_merged_graph, er_summarized_graph
