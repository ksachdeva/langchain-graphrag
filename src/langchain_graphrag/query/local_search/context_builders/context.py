from langchain_core.documents import Document

from langchain_graphrag.query.local_search.context_selectors import (
    ContextSelectionResult,
)

from .communities_reports import CommunitiesReportsContextBuilder
from .entities import EntitiesContextBuilder
from .relationships import RelationshipsContextBuilder
from .text_units import TextUnitsContextBuilder


class ContextBuilder:
    def __init__(
        self,
        entities_context_builder: EntitiesContextBuilder,
        realtionships_context_builder: RelationshipsContextBuilder,
        text_units_context_builder: TextUnitsContextBuilder,
        communities_reports_context_builder: CommunitiesReportsContextBuilder,
    ):
        self._entities_context_builder = entities_context_builder
        self._relationships_context_builder = realtionships_context_builder
        self._text_units_context_builder = text_units_context_builder
        self._communities_reports_context_builder = communities_reports_context_builder

    def __call__(self, result: ContextSelectionResult) -> list[Document]:
        entities_document = self._entities_context_builder(result.entities)
        relationships_document = self._relationships_context_builder(
            result.relationships
        )
        text_units_document = self._text_units_context_builder(result.text_units)
        communities_reports_document = self._communities_reports_context_builder(
            result.communities_reports
        )
        return [
            entities_document,
            relationships_document,
            text_units_document,
            communities_reports_document,
        ]
