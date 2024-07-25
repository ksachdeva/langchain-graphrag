from typing import Protocol
from pathlib import Path

from langchain_core.prompts import PromptTemplate
from langchain_graphrag.protocols import PromptBuilder


DEFAULT_TUPLE_DELIMITER = "<|>"
DEFAULT_RECORD_DELIMITER = "##"
DEFAULT_COMPLETION_DELIMITER = "<|COMPLETE|>"
DEFAULT_ENTITY_TYPES = ["organization", "person", "geo", "event"]


class DefaultEntityExtractionPromptBuilder(PromptBuilder):
    def __init__(
        self,
        prompt_path: Path,
        entity_types: list[str] = DEFAULT_ENTITY_TYPES,
        tuple_delimiter: str = DEFAULT_TUPLE_DELIMITER,
        record_delimiter: str = DEFAULT_RECORD_DELIMITER,
        completion_delimiter: str = DEFAULT_COMPLETION_DELIMITER,
    ):
        self._prompt_path = prompt_path
        self._entity_types = entity_types
        self._tuple_delimiter = tuple_delimiter
        self._record_delimiter = record_delimiter
        self._completion_delimiter = completion_delimiter

    def build(self) -> PromptTemplate:
        prompt_template = PromptTemplate.from_file(self._prompt_path)
        prompt_partial = prompt_template.partial(
            completion_delimiter=self._completion_delimiter,
            tuple_delimiter=self._tuple_delimiter,
            record_delimiter=self._record_delimiter,
            entity_types=self._entity_types,
        )
        return prompt_partial
