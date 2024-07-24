""" A module to extract text units from the document """

from typing import Sequence
from typing import TypedDict

import uuid

from tqdm import tqdm

from langchain_core.documents import Document
from langchain_text_splitters import TextSplitter


class TextUnit(TypedDict):
    document_id: str
    chunk_id: str
    chunk: str


class TextUnitExtractor:
    def __init__(self, text_splitter: TextSplitter):
        self._text_splitter = text_splitter

    def run(self, document: Document) -> Sequence[TextUnit]:
        text_units = self._text_splitter.split_text(document.page_content)

        document_id = document_id if document.id else str(uuid.uuid4())

        response: Sequence[TextUnit] = []
        for t in tqdm(text_units):
            response.append(
                TextUnit(document_id=document_id, chunk_id=str(uuid.uuid4()), chunk=t)
            )

        return response
