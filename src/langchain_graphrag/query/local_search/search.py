from pathlib import Path

import pandas as pd

from langchain_graphrag.types.graphs.community import CommunityLevel

from .context_selectors import ContextSelector


class LocalQuerySearch:
    def __init__(
        self,
        artifacts_dir: Path,
        community_level: CommunityLevel,
        context_selector: ContextSelector,
    ):
        self._artifacts_dir = artifacts_dir
        self._community_level = community_level
        self._context_selector = context_selector

    def invoke(self, query: str) -> str:
        df_entities = pd.read_parquet(self._artifacts_dir / "entities.parquet")
        df_text_units = pd.read_parquet(self._artifacts_dir / "text_units.parquet")
        df_relationships = pd.read_parquet(
            self._artifacts_dir / "relationships.parquet"
        )

        context_selection_result = self._context_selector.run(
            query=query,
            df_entities=df_entities,
            df_text_units=df_text_units,
            df_relationships=df_relationships,
        )

        print(context_selection_result.entities)
