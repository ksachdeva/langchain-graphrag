from langchain_graphrag.indexing.artifacts import IndexerArtifacts

from .context_builders import ContextBuilder
from .context_selectors import ContextSelector


class LocalQuerySearch:
    def __init__(
        self,
        context_selector: ContextSelector,
        context_builder: ContextBuilder,
    ):
        self._context_selector = context_selector
        self._context_builder = context_builder

    def invoke(self, query: str, artifacts: IndexerArtifacts) -> str:
        context_selection_result = self._context_selector.run(
            query=query,
            artifacts=artifacts,
        )

        documents = self._context_builder(context_selection_result)

        for d in documents:
            print(d.page_content)
