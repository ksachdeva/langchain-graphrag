from langchain_core.documents import Document

from langchain_graphrag.indexing.artifacts import IndexerArtifacts
from langchain_graphrag.query.global_search.community_report import CommunityReport
from langchain_graphrag.query.global_search.community_weight_calculator import (
    CommunityWeightCalculator,
)
from langchain_graphrag.types.graphs.community import CommunityId, CommunityLevel

_REPORT_TEMPLATE = """
--- Report {report_id} ---

Title: {title}
Weight: {weight}
Rank: {rank}
Report:

{content}

"""


class CommunityReportContextBuilder:
    def __init__(
        self,
        community_level: CommunityLevel,
        weight_calculator: CommunityWeightCalculator,
        artifacts: IndexerArtifacts,
    ):
        self._community_level = community_level
        self._weight_calculator = weight_calculator
        self._artifacts = artifacts

    def _filter_communities(self) -> list[CommunityReport]:
        df_entities = self._artifacts.entities
        df_reports = self._artifacts.communities_reports

        reports_weight: dict[CommunityId, float] = self._weight_calculator(
            df_entities,
            df_reports,
        )

        df_reports_filtered = df_reports[df_reports["level"] <= self._community_level]

        reports = []
        for _, row in df_reports_filtered.iterrows():
            reports.append(
                CommunityReport(
                    id=row["community_id"],
                    weight=reports_weight[row["community_id"]],
                    title=row["title"],
                    summary=row["summary"],
                    rank=row["rating"],
                    content=row["content"],
                )
            )

        return reports

    def __call__(self) -> list[Document]:
        reports = self._filter_communities()

        documents: list[Document] = []
        for report in reports:
            documents.append(  # noqa: PERF401
                Document(
                    page_content=_REPORT_TEMPLATE.format(
                        report_id=report.id,
                        title=report.title,
                        weight=report.weight,
                        rank=report.rank,
                        content=report.content,
                    )
                )
            )

        return documents
