from typing import Any

try:
    from langchain.output_parsers import PydanticOutputParser
except ImportError:
    # Langchain >= 1.0.0
    from langchain_core.output_parsers import PydanticOutputParser

from .utils import CommunityReportResult


class CommunityReportOutputParser(PydanticOutputParser):
    def __init__(self, **kwargs: dict[str, Any]):
        super().__init__(pydantic_object=CommunityReportResult, **kwargs)
