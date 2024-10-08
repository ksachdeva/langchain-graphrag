from pathlib import Path
from typing import Any

import networkx as nx
import pandas as pd
from langchain_core.output_parsers.base import BaseOutputParser
from langchain_core.prompts import BasePromptTemplate, PromptTemplate
from typing_extensions import Unpack

from langchain_graphrag.types.graphs.community import Community
from langchain_graphrag.types.prompts import IndexingPromptBuilder

from ._default_prompts import DEFAULT_PROMPT
from ._output_parser import CommunityReportOutputParser
from .utils import get_info


class CommunityReportGenerationPromptBuilder(IndexingPromptBuilder):
    def __init__(
        self,
        *,
        prompt: str | None = None,
        prompt_path: Path | None = None,
    ):
        self._prompt: str | None
        if prompt is None and prompt_path is None:
            self._prompt = DEFAULT_PROMPT
        else:
            self._prompt = prompt

        self._prompt_path = prompt_path

    def build(self) -> tuple[BasePromptTemplate, BaseOutputParser]:
        if self._prompt:
            prompt_template = PromptTemplate.from_template(self._prompt)
        else:
            assert self._prompt_path is not None
            prompt_template = PromptTemplate.from_file(self._prompt_path)

        return prompt_template, CommunityReportOutputParser()

    def prepare_chain_input(self, **kwargs: Unpack[dict[str, Any]]) -> dict[str, str]:
        community: Community = kwargs.get("community", None)
        graph: nx.Graph = kwargs.get("graph", None)

        if community is None:
            raise ValueError("community is required")

        if graph is None:
            raise ValueError("graph is required")

        entities, relationships = get_info(community, graph)

        entities_table = pd.DataFrame.from_records(entities).to_csv(
            index=False,
        )

        relationships_table = pd.DataFrame.from_records(relationships).to_csv(
            index=False,
        )

        input_text = f"""
        -----Entities-----
        {entities_table}

        -----Relationships-----
        {relationships_table}
        """

        return dict(input_text=input_text)
