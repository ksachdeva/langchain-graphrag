import networkx as nx
import pandas as pd
from tqdm import tqdm

from langchain_graphrag.indexing.report_generation import (
    CommunityReportGenerator,
    CommunityReportWriter,
)
from langchain_graphrag.types.graphs.community import (
    Community,
    CommunityDetectionResult,
)


class CommunitiesReportsTableGenerator:
    def __init__(
        self,
        report_generator: CommunityReportGenerator,
        report_writer: CommunityReportWriter,
    ):
        self._report_generator = report_generator
        self._report_writer = report_writer

    def _generate_report(self, community: Community, graph: nx.Graph) -> str:
        report = self._report_generator.invoke(community=community, graph=graph)
        return self._report_writer.write(report)

    def run(
        self,
        detection_result: CommunityDetectionResult,
        graph: nx.Graph,
    ) -> pd.DataFrame:
        reports = []

        for level in detection_result.communities:
            communities = detection_result.communities_at_level(level)
            c_pbar = tqdm(communities)
            for c in c_pbar:
                c_pbar.set_description_str(
                    f"Generating report for level={level} commnuity_id={c.id}"
                )
                report_str = self._generate_report(c, graph)

                reports.append(
                    dict(
                        level=level,
                        community_id=c.id,
                        report=report_str,
                    )
                )

        return pd.DataFrame.from_records(reports)
