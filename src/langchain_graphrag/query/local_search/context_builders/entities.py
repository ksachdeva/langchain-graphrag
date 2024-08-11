import pandas as pd
from langchain_core.documents import Document


class EntitiesContextBuilder:
    def __init__(
        self,
        *,
        include_rank: bool = True,
        context_name: str = "Entities",
        rank_heading: str = "number of relationships",
        column_delimiter: str = "|",
    ):
        self._include_rank = include_rank
        self._context_name = context_name
        self._rank_heading = rank_heading
        self._column_delimiter = column_delimiter

    def __call__(self, entities: pd.DataFrame) -> Document:
        current_context_text = f"-----{self._context_name}-----" + "\n"
        header = ["id", "entity", "description"]
        if self._include_rank:
            header.append(self._rank_heading)

        current_context_text += self._column_delimiter.join(header) + "\n"

        for entity in entities.itertuples():
            new_context = [
                str(entity.human_readable_id),
                entity.title,
                entity.description,
            ]
            if self._include_rank:
                new_context.append(str(entity.degree))

            new_context_text = self._column_delimiter.join(new_context) + "\n"
            current_context_text += new_context_text

        return Document(page_content=current_context_text)
