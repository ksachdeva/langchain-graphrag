from copy import deepcopy
import networkx as nx

from .node_position import GraphLayout


class PositionedGraphBuilder:
    def run(self, graph: nx.Graph, layout: GraphLayout) -> GraphLayout:
        positioned_graph = deepcopy(graph)
        for node_position in layout:
            if node_position.label not in positioned_graph.nodes:
                continue
            positioned_graph.nodes[node_position.label]["x"] = node_position.x
            positioned_graph.nodes[node_position.label]["y"] = node_position.y
            positioned_graph.nodes[node_position.label]["size"] = node_position.size

        return positioned_graph
