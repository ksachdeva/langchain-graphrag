""" This modules takes a graph and generater embedding for name and description of various entities """

import numpy as np
import networkx as nx

from tqdm import tqdm

from langchain_core.embeddings import Embeddings


class EntityEmbeddingGenerator:
    def __init__(self, embedding_model: Embeddings):
        self._embedding_model = embedding_model

    def run(self, graph: nx.Graph) -> dict[str, tuple[str, np.ndarray]]:
        # let's collect all the name and description of the nodes
        name_descriptions: list[tuple[str, str]] = []
        for name, description in graph.nodes(data="description"):
            name_descriptions.append((name, f"{name}:{description}"))

        # TODO: optimize this later to use the batch mode
        # instead of sequentially doing the embedding
        result: dict[str, tuple[str, np.ndarray]] = {}
        for name, name_description in tqdm(
            name_descriptions, desc="Generating Embeddings ..."
        ):
            document_embeddings = self._embedding_model.embed_documents(
                [name_description]
            )
            result[name] = (name_description, np.array(document_embeddings[0]))

        return result
