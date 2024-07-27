from typing import NewType
from typing import Sequence

from random import Random

import networkx as nx

from graspologic.partition import hierarchical_leiden
from graspologic.partition import HierarchicalCluster, HierarchicalClusters

from langchain_graphrag.utils.uuid import gen_uuid

from .utils import stable_largest_connected_component

CommunityLevel = NewType("CommunityLevel", int)
CommunityId = NewType("CommunityId", str)
NodeName = NewType("NodeName", str)
CommunityDetectionResult = dict[CommunityLevel, dict[CommunityId, list[NodeName]]]
Communities = list[tuple[CommunityLevel, CommunityId, list[NodeName]]]


def apply_level(
    source_graph: nx.Graph,
    communities: Communities,
    level: CommunityLevel,
    seed=0xF001,
) -> nx.Graph:
    random = Random(seed)  # noqa S311

    graph = source_graph.copy()

    for community_level, community_id, nodes in communities:
        if level != community_level:
            continue

        for node in nodes:
            graph.nodes[node]["cluster"] = community_id
            graph.nodes[node]["level"] = level

    # add node degree
    for node_degree in graph.degree:
        graph.nodes[str(node_degree[0])]["degree"] = int(node_degree[1])

    # add node uuid and incremental record id (a human readable id used as reference in the final report)
    for index, node in enumerate(graph.nodes()):
        graph.nodes[node]["human_readable_id"] = index
        graph.nodes[node]["id"] = str(gen_uuid(random))

    # add ids to edges
    for index, edge in enumerate(graph.edges()):
        graph.edges[edge]["id"] = str(gen_uuid(random))
        graph.edges[edge]["human_readable_id"] = index
        graph.edges[edge]["level"] = level

    return graph


def apply_clustering(
    source_graph: nx.Graph,
    levels: Sequence[CommunityLevel],
    communities: Communities,
) -> list[tuple[CommunityLevel, nx.Graph]]:
    graph_level_pairs: list[tuple[CommunityLevel, nx.Graph]] = []
    for level in levels:
        graph = apply_level(source_graph, communities, level)
        graph_level_pairs.append((level, graph))
    return graph_level_pairs


class HierarchicalLeidenCommunityDetector:
    def __init__(
        self,
        use_lcc: bool = True,
        max_cluster_size: int = 10,
        seed: int = 0xDEADBEEF,
    ):
        self._use_lcc = use_lcc
        self._max_cluster_size = max_cluster_size
        self._seed = seed

    def run(self, graph: nx.Graph) -> list[tuple[CommunityLevel, nx.Graph]]:
        if self._use_lcc:
            graph = stable_largest_connected_component(graph)

        community_mapping: HierarchicalClusters = hierarchical_leiden(
            graph,
            max_cluster_size=self._max_cluster_size,
            random_seed=self._seed,
        )

        results: dict[int, dict[str, int]] = {}

        partition: HierarchicalCluster
        for partition in community_mapping:
            results[partition.level] = results.get(partition.level, {})
            results[partition.level][partition.node] = partition.cluster

        levels = sorted(results.keys())

        results_by_level: CommunityDetectionResult = {}
        for level in levels:
            result = {}
            results_by_level[level] = result
            for node_id, raw_community_id in results[level].items():
                community_id = str(raw_community_id)
                if community_id not in result:
                    result[community_id] = []
                result[community_id].append(node_id)

        communities: Communities = []
        for level in results_by_level:
            for cluster_id, nodes in results_by_level[level].items():
                communities.append((level, cluster_id, nodes))

        # time to apply clustering
        graph_level_pairs = apply_clustering(graph, levels, communities)

        return graph_level_pairs
