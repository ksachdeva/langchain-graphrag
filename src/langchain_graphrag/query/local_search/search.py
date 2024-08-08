from langchain_graphrag.indexing.artifacts import IndexerArtifacts
from langchain_graphrag.types.graphs.community import CommunityLevel

from .context_selectors import ContextSelector


class LocalQuerySearch:
    def __init__(
        self,
        community_level: CommunityLevel,
        context_selector: ContextSelector,
    ):
        self._community_level = community_level
        self._context_selector = context_selector

    def invoke(self, query: str, artifacts: IndexerArtifacts) -> str:
        context_selection_result = self._context_selector.run(
            query=query,
            artifacts=artifacts,
        )
