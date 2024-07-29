import os
from pathlib import Path

import networkx as nx

from .create_final_communities import FinalCommunitiesGenerator

# CLUSTERED_GRAPH_TEST_DIR = Path(os.environ["CLUSTERED_GRAPH_TEST_DIR"])
CLUSTERED_GRAPH_TEST_DIR = Path(
    "/workspaces/langchain-graphrag/test-data/clustered-graphs"
)


def test_basic():
    clustered_graphs = [
        (level, nx.read_graphml(f"{CLUSTERED_GRAPH_TEST_DIR}/level_{level}.graphml"))
        for level in [0, 1, 2]
    ]

    final_communities_generator = FinalCommunitiesGenerator()
    final_communities_generator.run(clustered_graphs)
