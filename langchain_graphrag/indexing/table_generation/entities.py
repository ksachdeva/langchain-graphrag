import numpy as np
import pandas as pd
import networkx as nx

from langchain_graphrag.indexing.entity_embedding import EntityEmbeddingGenerator
from langchain_graphrag.indexing.graph_embedding import (
    Node2VectorGraphEmbeddingGenerator,
)


class EntitiesTableGenerator:
    def __init__(
        self,
        entity_embedding_generator: EntityEmbeddingGenerator,
        graph_embedding_generator: Node2VectorGraphEmbeddingGenerator,
    ):
        self._entity_embedding_generator = entity_embedding_generator
        self._graph_embedding_generator = graph_embedding_generator

    def _unpack_nodes(
        self,
        graph: nx.Graph,
        name_description_embeddings: dict[str, np.ndarray],
        graph_embeddings: dict[str, np.ndarray],
    ) -> pd.DataFrame:
        records = [
            {
                "title": label,
                **(node_data or {}),
                "graph_embedding": graph_embeddings.get(label),
                "name_description_embedding": name_description_embeddings.get(label),
            }
            for label, node_data in graph.nodes(data=True)
        ]
        return pd.DataFrame.from_records(records)

    def run(self, graph: nx.Graph) -> pd.DataFrame:

        # Step 1
        # Generate graph embeddings
        graph_embeddings = self._graph_embedding_generator.run(graph)

        # Step 2
        # Generate entity embeddings for name:description combination
        name_description_embeddings = self._entity_embedding_generator.run(graph)

        # Step 3
        # Make a dataframe with embeddings & other information
        df = self._unpack_nodes(graph, name_description_embeddings, graph_embeddings)

        return df
