from typing import Any

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from langchain_graphrag.query.global_search.community_report import CommunityReport
from langchain_graphrag.query.global_search.key_points_generator.utils import (
    KeyPointInfo,
    KeyPointsResult,
)
from langchain_graphrag.types.prompts import PromptBuilder

from .system_prompt import REDUCE_SYSTEM_PROMPT

_REPORT_TEMPLATE = """
--- Analyst {analyst_id} ---

Importance Score: {score}

{content}

"""


class DefaultAggregatorPromptBuilder(PromptBuilder):
    def __init__(self, prompt: str | None = None):
        self._system_prompt = prompt if prompt is not None else REDUCE_SYSTEM_PROMPT

    def build(self) -> PromptTemplate:
        return ChatPromptTemplate(
            [("system", self._system_prompt), ("user", "{global_query}")]
        )

    def prepare_chain_input(self, **kwargs: dict[str, Any]) -> dict[str, str]:
        global_query = kwargs.get("global_query", None)
        key_points: list[KeyPointsResult] = kwargs.get("key_points", [])

        if global_query is None:
            raise ValueError("global_query is required")

        if not key_points:
            raise ValueError("key_points is required")

        # prepare context_data from key points
        kp_strs = []
        for kp_index, kp in enumerate(key_points):
            for p in kp.points:
                kp_strs.append(  # noqa: PERF401
                    _REPORT_TEMPLATE.format(
                        analyst_id=(kp_index + 1),
                        score=p.score,
                        content=p.description,
                    )
                )

        report_data = "\n".join(kp_strs)

        return dict(
            response_type="Multiple Paragraphs",
            report_data=report_data,
            global_query=global_query,
        )
