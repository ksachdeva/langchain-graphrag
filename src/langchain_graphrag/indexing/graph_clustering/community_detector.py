from typing import NewType
from typing import Sequence

from copy import deepcopy
import networkx as nx

from graspologic.partition import hierarchical_leiden
from graspologic.partition import HierarchicalCluster, HierarchicalClusters

from langchain_graphrag.utils.uuid import gen_uuid
from langchain_graphrag.graph_utils.stable_lcc import stable_largest_connected_component

CommunityLevel = NewType("CommunityLevel", int)
CommunityId = NewType("CommunityId", str)
NodeName = NewType("NodeName", str)
CommunityDetectionResult = dict[CommunityLevel, dict[CommunityId, list[NodeName]]]
Communities = list[tuple[CommunityLevel, CommunityId, list[NodeName]]]


def apply_level(
    source_graph: nx.Graph,
    communities: Communities,
    level: CommunityLevel,
) -> nx.Graph:

    graph = deepcopy(source_graph)

    # TODO: Revist - do we really need this
    # as we will have a map of level & graph anyways
    # add level to nodes
    for node in graph.nodes():
        graph.nodes[node]["level"] = level

    # TODO: Revist - do we really need this
    # as we will have a map of level & graph anyways
    # add level to edges
    for edge in graph.edges():
        graph.edges[edge]["level"] = level

    for community_level, community_id, nodes in communities:
        if level != community_level:
            continue

        # add the community_id to the nodes
        # as the cluster
        for node in nodes:
            graph.nodes[node]["cluster"] = community_id

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

        # Below could be re-written

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
