from pathlib import Path
from typing import Any

from langchain_core.output_parsers.base import BaseOutputParser
from langchain_core.prompts import (
    BasePromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)
from typing_extensions import Unpack

from langchain_graphrag.query.global_search.community_report import CommunityReport
from langchain_graphrag.types.prompts import PromptBuilder

from .output_parser import KeyPointsOutputParser
from .system_prompt import MAP_SYSTEM_PROMPT

_REPORT_TEMPLATE = """
--- Report {report_id} ---

Title: {title}
Weight: {weight}
Rank: {rank}
Report:

{content}

"""


class KeyPointsGeneratorPromptBuilder(PromptBuilder):
    def __init__(
        self,
        *,
        system_prompt: str | None = None,
        system_prompt_path: Path | None = None,
    ):
        self._system_prompt: str | None
        if system_prompt is None and system_prompt_path is None:
            self._system_prompt = MAP_SYSTEM_PROMPT
        else:
            self._system_prompt = system_prompt

        self._system_prompt_path = system_prompt_path

    def build(self) -> tuple[BasePromptTemplate, BaseOutputParser]:
        if self._system_prompt:
            system_template = SystemMessagePromptTemplate.from_template(
                self._system_prompt
            )
        else:
            assert self._system_prompt_path is not None
            system_template = SystemMessagePromptTemplate.from_template_file(
                self._system_prompt_path,
                input_variables=["context_data"],
            )

        template = ChatPromptTemplate([system_template, ("user", "{global_query}")])
        output_parser = KeyPointsOutputParser()

        return template, output_parser

    def prepare_chain_input(self, **kwargs: Unpack[dict[str, Any]]) -> dict[str, str]:
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
