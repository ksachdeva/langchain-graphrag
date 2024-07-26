from typing import TypedDict, TypeAlias, NewType

import networkx as nx

from graspologic.partition import hierarchical_leiden
from graspologic.partition import HierarchicalCluster, HierarchicalClusters

from .utils import stable_largest_connected_component

CommunityLevel = NewType("CommunityLevel", int)
CommunityId = NewType("CommunityId", str)
NodeName = NewType("NodeName", str)
CommunityDetectionResult = dict[CommunityLevel, dict[CommunityId, list[NodeName]]]


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

    def run(self, graph: nx.Graph) -> CommunityDetectionResult:
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

        return results_by_level
