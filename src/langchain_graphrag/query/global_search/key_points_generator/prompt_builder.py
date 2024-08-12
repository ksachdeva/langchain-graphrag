from typing import Any
from pathlib import Path

from langchain_core.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)

from langchain_graphrag.query.global_search.community_report import CommunityReport
from langchain_graphrag.types.prompts import PromptBuilder

from .system_prompt import MAP_SYSTEM_PROMPT

_REPORT_TEMPLATE = """
--- Report {report_id} ---

Title: {title}
Weight: {weight}
Rank: {rank}
Report:

{content}

"""


class DefaultKeyPointsGeneratorPromptBuilder(PromptBuilder):
    def __init__(
        self,
        *,
        system_prompt: str | None = None,
        system_prompt_path: Path | None = None,
    ):
        if system_prompt is None and system_prompt_path is None:
            self._system_prompt = MAP_SYSTEM_PROMPT
        else:
            self._system_prompt = system_prompt
            self._system_prompt_path = system_prompt_path

    def build(self) -> PromptTemplate:
        system_template = (
            SystemMessagePromptTemplate.from_template(self._system_prompt)
            if self._system_prompt
            else SystemMessagePromptTemplate.from_file(self._system_prompt_path)
        )

        return ChatPromptTemplate([system_template, ("user", "{global_query}")])

    def prepare_chain_input(self, **kwargs: dict[str, Any]) -> dict[str, str]:
        global_query = kwargs.get("global_query", None)
        reports: list[CommunityReport] = kwargs.get("reports", [])

        if global_query is None:
            raise ValueError("global_query is required")

        if not reports:
            raise ValueError("reports is required")

        # prepare context_data from reports
        report_strs = []
        for report in reports:
            report_strs.append(  # noqa: PERF401
                _REPORT_TEMPLATE.format(
                    report_id=report.id,
                    title=report.title,
                    weight=report.weight,
                    rank=report.rank,
                    content=report.content,
                )
            )

        context_data = "\n".join(report_strs)

        return dict(context_data=context_data, global_query=global_query)
