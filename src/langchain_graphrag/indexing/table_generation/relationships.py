import networkx as nx
import pandas as pd
from langchain_core.vectorstores import VectorStore


class RelationshipsTableGenerator:
    def __init__(
        self,
        relationships_vector_store: VectorStore,
    ):
        self._relationships_vector_store = relationships_vector_store

    def _unpack_edges(self, graph: nx.Graph) -> pd.DataFrame:
        records = [
            {
                "source": source_id,
                "target": target_id,
                **(edge_data or {}),
            }
            for source_id, target_id, edge_data in graph.edges(data=True)
        ]
        return pd.DataFrame.from_records(records)

    def run(self, graph: nx.Graph) -> pd.DataFrame:
        # Step 1
        # Extract the information to embed from the graph
        # and put in the vectorstore
        texts_to_embed = []
        texts_metadata = []
        texts_ids = []
        for source, target, edge_data in graph.edges(data=True):
            text_description = edge_data.get("description")
            texts_ids.append(edge_data.get("id"))
            texts_to_embed.append(text_description)

            # Bug in langchain vectorstore retrival that
            # does not populate Document.id field.
            #
            # Hence add relationship_id as an additional field
            # in the metadata
            texts_metadata.append(
                dict(
                    source=source,
                    target=target,
                    description=text_description,
                    rank=edge_data.get("rank"),
                    relationship_id=edge_data.get(
                        "id"
                    ),  # TODO: Remove once langchain is fixed
                )
            )

        self._relationships_vector_store.add_texts(
            texts_to_embed,
            metadatas=texts_metadata,
            ids=texts_ids,
        )

        # Step 2
        # Make a dataframe
        return self._unpack_edges(graph)
