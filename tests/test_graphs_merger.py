import networkx as nx

from langchain_graphrag.indexing.graph_generation.graphs_merger import (
    merge_edges,
    merge_nodes,
)


def test_node_merge():
    target_graph = nx.Graph()

    graph1 = nx.Graph()
    graph1.add_node("node1", text_unit_ids=["1"], description=[" "])
    graph1.add_node("node2", text_unit_ids=["2"], description=["description2"])
    graph1.add_node("node3", text_unit_ids=["3"], description=["description3"])

    graph1.add_edge(
        "node1",
        "node2",
        text_unit_ids=["1"],
        description=["edge description1"],
        weight=2,
    )

    graph2 = nx.Graph()
    graph2.add_node(
        "node1", text_unit_ids=["4"], description=["description1 from graph2"]
    )
    graph2.add_node(
        "node2", text_unit_ids=["5"], description=["description2 from graph2"]
    )
    graph2.add_node(
        "node4", text_unit_ids=["6"], description=["description4 from graph2"]
    )

    graph2.add_edge(
        "node1",
        "node2",
        text_unit_ids=["9"],
        description=["edge description1"],
        weight=4,
    )

    merge_nodes(target_graph=target_graph, sub_graph=graph1)
    merge_edges(target_graph=target_graph, sub_graph=graph1)

    merge_nodes(target_graph=target_graph, sub_graph=graph2)
    merge_edges(target_graph=target_graph, sub_graph=graph2)

    print(target_graph.nodes(data=True))
    print(target_graph.edges(data=True))
