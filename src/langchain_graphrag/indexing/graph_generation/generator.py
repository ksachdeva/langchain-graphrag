import pandas as pd
import networkx as nx

from .entity_relationship_extraction import EntityRelationshipExtractor
from .entity_relationship_summarization import EntityRelationshipDescriptionSummarizer


class GraphGenerator:
    def __init__(
        self,
        er_extractor: EntityRelationshipExtractor,
        er_description_summarizer: EntityRelationshipDescriptionSummarizer,
    ):
        self._er_extractor = er_extractor
        self._er_description_summarizer = er_description_summarizer

    def run(self, text_units: pd.DataFrame) -> nx.Graph:
        er_graph = self._er_extractor.invoke(text_units)
        er_graph_summarized = self._er_description_summarizer.invoke(er_graph)

        return er_graph_summarized
