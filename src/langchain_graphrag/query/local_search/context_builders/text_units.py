import pandas as pd
from langchain_core.documents import Document


class TextUnitsContextBuilder:
    def __init__(
        self,
        *,
        context_name: str = "Sources",
        column_delimiter: str = "|",
    ):
        self._context_name = context_name
        self._column_delimiter = column_delimiter

    def __call__(self, text_units: pd.DataFrame) -> Document:
        current_context_text = f"-----{self._context_name}-----" + "\n"
        header = ["id", "text"]

        current_context_text += self._column_delimiter.join(header) + "\n"

        for text_unit in text_units.itertuples():
            new_context = [str(text_unit.short_id), text_unit.text]
            new_context_text = self._column_delimiter.join(new_context) + "\n"
            current_context_text += new_context_text

        return Document(page_content=current_context_text)
