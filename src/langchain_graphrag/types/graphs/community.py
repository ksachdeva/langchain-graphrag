from dataclasses import dataclass
from typing import NewType, Protocol

import networkx as nx

CommunityId = NewType("CommunityId", int)
CommunityLevel = NewType("CommunityLevel", int)


@dataclass
class CommunityNode:
    name: str
    parent_cluster: CommunityId | None
    is_final_cluster: bool


@dataclass
class Community:
    id: CommunityId
    nodes: list[CommunityNode]


@dataclass
class CommunityDetectionResult:
    communities: dict[CommunityLevel, dict[CommunityId, Community]]


class CommunityDetector(Protocol):
    def run(self, graph: nx.Graph) -> CommunityDetectionResult: ...
