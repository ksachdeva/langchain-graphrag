from pathlib import Path

from langchain_core.prompts import PromptTemplate

from langchain_graphrag.protocols import PromptBuilder


class DefaultSummarizeDescriptionPromptBuilder(PromptBuilder):
    def __init__(self, prompt_path: Path):
        self._prompt_path = prompt_path

    def build(self) -> PromptTemplate:
        return PromptTemplate.from_file(self._prompt_path)
