from typing import Any

import re
import html
import numbers

from collections.abc import Mapping

import networkx as nx
from langchain_core.output_parsers import BaseOutputParser

from .prompt import DEFAULT_RECORD_DELIMITER, DEFAULT_TUPLE_DELIMITER


def _clean_str(input: Any) -> str:
    """Clean an input string by removing HTML escapes, control characters, and other unwanted characters."""
    # If we get non-string input, just give it back
    if not isinstance(input, str):
        return input

    result = html.unescape(input.strip())
    # https://stackoverflow.com/questions/4324790/removing-control-characters-from-a-string-in-python
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", result)


def _unpack_descriptions(data: Mapping) -> list[str]:
    value = data.get("description", None)
    # ignore if value is not str
    if not isinstance(value, str):
        return []
    return [] if value is None else value.split("\n")


class EntityExtractionOutputParser(BaseOutputParser[nx.Graph]):
    tuple_delimiter: str = DEFAULT_TUPLE_DELIMITER
    record_delimiter: str = DEFAULT_TUPLE_DELIMITER

    def __init__(
        self,
        tuple_delimiter: str = DEFAULT_TUPLE_DELIMITER,
        record_delimiter: str = DEFAULT_RECORD_DELIMITER,
    ):
        super().__init__()
        self.tuple_delimiter = tuple_delimiter
        self.record_delimiter = record_delimiter

    def _process_entity(self, record_attributes: list[str], graph: nx.Graph):
        if record_attributes[0] != '"entity"' or len(record_attributes) < 4:
            return

        # add this record as a node in the G
        entity_name = _clean_str(record_attributes[1].upper())
        entity_type = _clean_str(record_attributes[2].upper())
        entity_description = _clean_str(record_attributes[3])

        if entity_name in graph.nodes():
            node = graph.nodes[entity_name]
            node["description"] = list(
                {
                    *_unpack_descriptions(node),
                    entity_description,
                }
            )

            node["entity_type"] = (
                entity_type if entity_type != "" else node["entity_type"]
            )
        else:
            graph.add_node(
                entity_name,
                type=entity_type,
                description=[entity_description],
            )

    def _process_relationship(self, record_attributes: list[str], graph: nx.Graph):
        if record_attributes[0] != '"relationship"' or len(record_attributes) < 5:
            return

        # add this record as edge
        source = _clean_str(record_attributes[1].upper())
        target = _clean_str(record_attributes[2].upper())
        edge_description = _clean_str(record_attributes[3])

        weight = (
            float(record_attributes[-1])
            if isinstance(record_attributes[-1], numbers.Number)
            else 1.0
        )
        if source not in graph.nodes():
            graph.add_node(
                source,
                type="",
                description=[""],
            )
        if target not in graph.nodes():
            graph.add_node(
                target,
                type="",
                description=[""],
            )
        if graph.has_edge(source, target):
            edge_data = graph.get_edge_data(source, target)
            if edge_data is not None:
                weight += edge_data["weight"]
                edge_description = list(
                    {
                        *_unpack_descriptions(edge_data),
                        edge_description,
                    }
                )

        graph.add_edge(source, target, weight=weight, description=[edge_description])

    def _process_record(self, graph: nx.Graph, record: str):
        record = re.sub(r"^\(|\)$", "", record.strip())
        record_attributes = record.split(self.tuple_delimiter)

        self._process_entity(record_attributes, graph)
        self._process_relationship(record_attributes, graph)

    def parse(self, text: str) -> nx.Graph:
        graph = nx.Graph()
        records = [r.strip() for r in text.split(self.record_delimiter)]
        for record in records:
            self._process_record(graph, record)
        return graph

    @property
    def _type(self) -> str:
        return "entity_extraction_output_parser"
