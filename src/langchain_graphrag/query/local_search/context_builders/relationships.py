import pandas as pd
from langchain_core.documents import Document

from langchain_graphrag.query.local_search.context_selectors.relationships import (
    RelationshipsSelectionResult,
)


class RelationshipsContextBuilder:
    def __init__(
        self,
        *,
        include_weight: bool = True,
        context_name: str = "Relationships",
        column_delimiter: str = "|",
    ):
        self._include_weight = include_weight
        self._context_name = context_name
        self._column_delimiter = column_delimiter

    def __call__(
        self,
        selected_relationships: RelationshipsSelectionResult,
    ) -> Document:
        current_context_text = f"-----{self._context_name}-----" + "\n"
        header = ["id", "source", "target", "description"]
        if self._include_weight:
            header.append("weight")

        current_context_text += self._column_delimiter.join(header) + "\n"

        def _build_context_text(
            relationships: pd.DataFrame,
            context_text: str,
        ) -> None:
            for relationship in relationships.itertuples():
                new_context = [
                    str(relationship.human_readable_id),
                    relationship.source,
                    relationship.target,
                    relationship.description,
                ]
                if self._include_weight:
                    new_context.append(str(relationship.weight))

                new_context_text = self._column_delimiter.join(new_context) + "\n"
                context_text += new_context_text

            return context_text

        current_context_text = _build_context_text(
            selected_relationships.in_network_relationships,
            current_context_text,
        )
        current_context_text = _build_context_text(
            selected_relationships.out_network_relationships,
            current_context_text,
        )

        return Document(page_content=current_context_text)
