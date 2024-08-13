from pathlib import Path
from typing import Any

from langchain_core.prompts import (
    BasePromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
)
from typing_extensions import Unpack

from langchain_graphrag.query.global_search.key_points_generator.utils import (
    KeyPointsResult,
)
from langchain_graphrag.types.prompts import PromptBuilder

from .system_prompt import REDUCE_SYSTEM_PROMPT

_REPORT_TEMPLATE = """
--- Analyst {analyst_id} ---

Importance Score: {score}

{content}

"""


class KeyPointsAggregatorPromptBuilder(PromptBuilder):
    def __init__(
        self,
        *,
        system_prompt: str | None = None,
        system_prompt_path: Path | None = None,
    ):
        self._system_prompt: str | None
        if system_prompt is None and system_prompt_path is None:
            self._system_prompt = REDUCE_SYSTEM_PROMPT
        else:
            self._system_prompt = system_prompt

        self._system_prompt_path = system_prompt_path

    def build(self) -> BasePromptTemplate:
        if self._system_prompt:
            system_template = SystemMessagePromptTemplate.from_template(
                self._system_prompt
            )
        else:
            assert self._system_prompt_path is not None
            system_template = SystemMessagePromptTemplate.from_template_file(
                self._system_prompt_path,
                input_variables=["response_type", "report_data"],
            )

        return ChatPromptTemplate([system_template, ("user", "{global_query}")])

    def prepare_chain_input(self, **kwargs: Unpack[dict[str, Any]]) -> dict[str, str]:
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
