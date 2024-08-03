import networkx as nx
import numpy as np
import pandas as pd

from langchain_graphrag.indexing.embedding_generation import (
    RelationshipEmbeddingGenerator,
)


class RelationshipsTableGenerator:
    def __init__(
        self,
        relationship_embedding_generator: RelationshipEmbeddingGenerator,
    ):
        self._relationship_embedding_generator = relationship_embedding_generator

    def _unpack_edges(
        self,
        graph: nx.Graph,
        description_embeddings: dict[str, np.ndarray],
    ) -> pd.DataFrame:
        records = [
            {
                "source": source_id,
                "target": target_id,
                **(edge_data or {}),
                "description_embeddings": description_embeddings.get(
                    f"{source_id}-{target_id}"
                ),
            }
            for source_id, target_id, edge_data in graph.edges(data=True)
        ]
        return pd.DataFrame.from_records(records)

    def run(self, graph: nx.Graph) -> pd.DataFrame:
        # Step 1
        # Generate embeddings for the description of edges
        description_embeddings = self._relationship_embedding_generator.run(graph)

        # Step 2
        # Make a dataframe with embeddings & other information
        return self._unpack_edges(graph, description_embeddings)
