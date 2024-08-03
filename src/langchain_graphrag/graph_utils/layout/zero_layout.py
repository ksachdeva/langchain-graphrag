import networkx as nx

from .node_position import GraphLayout, NodePosition


def get_zero_positions(
    *,
    node_labels: list[str],
    node_categories: list[int] | None = None,
    node_sizes: list[int] | None = None,
    three_d: bool | None = False,
) -> list[NodePosition]:
    """Project embedding vectors down to 2D/3D using UMAP."""
    embedding_position_data: list[NodePosition] = []
    for index, node_name in enumerate(node_labels):
        node_category = 1 if node_categories is None else node_categories[index]
        node_size = 1 if node_sizes is None else node_sizes[index]

        if not three_d:
            embedding_position_data.append(
                NodePosition(
                    label=str(node_name),
                    x=0,
                    y=0,
                    cluster=str(int(node_category)),
                    size=int(node_size),
                )
            )
        else:
            embedding_position_data.append(
                NodePosition(
                    label=str(node_name),
                    x=0,
                    y=0,
                    z=0,
                    cluster=str(int(node_category)),
                    size=int(node_size),
                )
            )
    return embedding_position_data


class ZeroLayout:
    def run(self, graph: nx.Graph) -> GraphLayout:
        node_clusters = []
        node_sizes = []

        nodes = list(graph.nodes)

        for node_id in nodes:
            node = graph.nodes[node_id]
            cluster = node.get("cluster", node.get("community", -1))
            node_clusters.append(cluster)
            size = node.get("degree", node.get("size", 0))
            node_sizes.append(size)

        additional_args = {}
        if len(node_clusters) > 0:
            additional_args["node_categories"] = node_clusters
        if len(node_sizes) > 0:
            additional_args["node_sizes"] = node_sizes

        return get_zero_positions(node_labels=nodes, **additional_args)
