from typing import Any

import itertools
from enum import StrEnum

import networkx as nx


class AttributesToMerge(StrEnum):
    text_unit_ids = "text_unit_ids"
    description = "description"
    weight = "weight"


def merge_attributes(
    *,
    target_node: dict[str, Any],
    source_node: dict[str, Any],
    attribs: list[AttributesToMerge],
):
    # separator = ", "
    for attrib in attribs:
        # I am expecting the attributes are not missing
        target_attrib = target_node.get(attrib)
        source_attrib = source_node.get(attrib)
        if attrib == AttributesToMerge.weight:
            target_node[attrib] = int(target_attrib) + int(source_attrib)
        else:
            target_node[attrib].extend(source_attrib)
            # REVISIT: Not sure why sometimes we end up
            # having list of list
            # make sure to flatten it
            target_node[attrib] = itertools.chain(*target_node[attrib])
            # now make sure to remove duplicates
            target_node[attrib] = sorted(set(target_node[attrib]))


def merge_nodes(*, target_graph: nx.Graph, sub_graph: nx.Graph):
    for node in sub_graph.nodes:
        if node not in target_graph.nodes:
            target_graph.add_node(node, **(sub_graph.nodes[node] or {}))
        else:
            merge_attributes(
                target_node=target_graph.nodes[node],
                source_node=sub_graph.nodes[node],
                attribs=[
                    AttributesToMerge.text_unit_ids,
                    AttributesToMerge.description,
                ],
            )


def merge_edges(*, target_graph: nx.Graph, sub_graph: nx.Graph):
    for source, target, edge_data in sub_graph.edges(data=True):  # type: ignore
        if not target_graph.has_edge(source, target):
            target_graph.add_edge(source, target, **(edge_data or {}))
        else:
            merge_attributes(
                target_node=target_graph.edges[(source, target)],
                source_node=edge_data,
                attribs=[
                    AttributesToMerge.text_unit_ids,
                    AttributesToMerge.description,
                    AttributesToMerge.weight,
                ],
            )


class GraphsMerger:
    def __call__(self, graphs: list[nx.Graph]) -> nx.Graph:
        merged_graph = nx.Graph()
        for graph in graphs:
            merge_nodes(target_graph=merged_graph, sub_graph=graph)
            merge_edges(target_graph=merged_graph, sub_graph=graph)
        return merged_graph
