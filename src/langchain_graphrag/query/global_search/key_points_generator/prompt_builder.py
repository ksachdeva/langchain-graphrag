from typing import Any

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

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
    def __init__(self, prompt: str | None = None):
        self._system_prompt = prompt if prompt is not None else MAP_SYSTEM_PROMPT

    def build(self) -> PromptTemplate:
        return ChatPromptTemplate(
            [("system", self._system_prompt), ("user", "{global_query}")]
        )

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
