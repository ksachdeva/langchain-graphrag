"""A module to extract text units from the document."""

import uuid
from typing import Sequence, TypedDict

import pandas as pd
from langchain_core.documents import Document
from langchain_text_splitters import TextSplitter
from tqdm import tqdm


class TextUnit(TypedDict):
    id: str
    document_id: str
    text: str


class TextUnitExtractor:
    def __init__(self, text_splitter: TextSplitter):
        self._text_splitter = text_splitter

    def run(self, document: Document) -> pd.DataFrame:
        text_units = self._text_splitter.split_text(document.page_content)

        document_id = document.id if document.id else str(uuid.uuid4())

        response: Sequence[TextUnit] = []
        for t in tqdm(text_units):
            response.append(
                TextUnit(document_id=document_id, id=str(uuid.uuid4()), text=t)
            )

        return pd.DataFrame.from_records(response)
