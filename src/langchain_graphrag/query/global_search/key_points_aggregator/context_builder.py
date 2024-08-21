from langchain_core.documents import Document

from langchain_graphrag.query.global_search.key_points_generator.utils import (
    KeyPointsResult,
)

_REPORT_TEMPLATE = """
--- {analyst} ---

Importance Score: {score}

{content}

"""


class KeyPointsContextBuilder:
    def __call__(self, key_points: dict[str, KeyPointsResult]) -> list[Document]:
        documents: list[Document] = []
        for k, v in key_points.items():
            for p in v.points:
                report = _REPORT_TEMPLATE.format(
                    analyst=k,
                    score=p.score,
                    content=p.description,
                )
                documents.append(Document(page_content=report))

        return documents
