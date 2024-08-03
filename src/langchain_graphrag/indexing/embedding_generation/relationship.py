"""Embedding generation for the relationship descriptions in the graph."""

import networkx as nx
import numpy as np
from langchain_core.embeddings import Embeddings
from tqdm import tqdm


class RelationshipEmbeddingGenerator:
    def __init__(self, embedding_model: Embeddings):
        self._embedding_model = embedding_model

    def run(self, graph: nx.Graph) -> dict[str, np.ndarray]:
        # let's collect all the name and description of the nodes
        edge_descriptions: list[tuple[str, str]] = []
        for source_id, target_id, description in graph.edges(data="description"):
            edge_id = f"{source_id}-{target_id}"
            edge_descriptions.append((edge_id, description))

        # TODO: optimize this later to use the batch mode
        # instead of sequentially doing the embedding
        result: dict[str, np.ndarray] = {}
        for edge_id, description in tqdm(
            edge_descriptions, desc="Generating Embeddings ..."
        ):
            document_embeddings = self._embedding_model.embed_documents([description])
            result[edge_id] = np.array(document_embeddings[0])

        return result
