from langchain_core.language_models import BaseLLM
from langchain_core.output_parsers.base import BaseOutputParser

from langchain_graphrag.indexing.artifacts import IndexerArtifacts

from .context_builders import ContextBuilder
from .context_selectors import ContextSelector
from .prompt_builder import LocalSearchPromptBuilder


class LocalSearch:
    def __init__(
        self,
        prompt_builder: LocalSearchPromptBuilder,
        llm: BaseLLM,
        output_parser: BaseOutputParser,
        context_selector: ContextSelector,
        context_builder: ContextBuilder,
    ):
        self._prompt_builder = prompt_builder
        self._context_selector = context_selector
        self._context_builder = context_builder

        prompt = prompt_builder.build()
        self._chain = prompt | llm | output_parser
        self._prompt_builder = prompt_builder

    def invoke(self, query: str, artifacts: IndexerArtifacts) -> str:
        context_selection_result = self._context_selector.run(
            query=query,
            artifacts=artifacts,
        )

        documents = self._context_builder(context_selection_result)

        chain_input = self._prompt_builder.prepare_chain_input(
            local_query=query,
            documents=documents,
        )

        return self._chain.invoke(input=chain_input)
