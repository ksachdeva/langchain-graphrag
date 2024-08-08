from pathlib import Path
from typing import NamedTuple

import pandas as pd
import tableprint


class IndexerArtifacts(NamedTuple):
    entities: pd.DataFrame
    relationships: pd.DataFrame
    text_units: pd.DataFrame
    communities: pd.DataFrame
    communities_reports: pd.DataFrame

    def save(self, path: Path):
        self.entities.to_parquet(f"{path}/entities.parquet")
        self.relationships.to_parquet(f"{path}/relationships.parquet")
        self.text_units.to_parquet(f"{path}/text_units.parquet")
        self.communities.to_parquet(f"{path}/communities.parquet")
        self.communities_reports.to_parquet(f"{path}/communities_reports.parquet")

    @staticmethod
    def load(path: Path) -> "IndexerArtifacts":
        entities = pd.read_parquet(f"{path}/entities.parquet")
        relationships = pd.read_parquet(f"{path}/relationships.parquet")
        text_units = pd.read_parquet(f"{path}/text_units.parquet")
        communities = pd.read_parquet(f"{path}/communities.parquet")
        communities_reports = pd.read_parquet(f"{path}/communities_reports.parquet")

        return IndexerArtifacts(
            entities,
            relationships,
            text_units,
            communities,
            communities_reports,
        )

    def _entity_info(self, top_k: int) -> None:
        tableprint.banner("Entities")

        rows = [
            ["Count", len(self.entities)],
            ["Number of types", len(self.entities["type"].unique())],
        ]
        tableprint.table(rows)

        # entity types
        tableprint.banner("Entity Types")
        rows = []
        for entity_type, count in self.entities["type"].value_counts().items():
            rows.append([entity_type, count])
        tableprint.table(rows, ["Type", "Count"])

        # k most connected entities
        by_degree = self.entities.sort_values("degree", ascending=False)[:top_k]

        # print k most connected entities
        tableprint.banner(f"{top_k} Most Connected Entities")
        tableprint.dataframe(by_degree[["title", "degree"]])

    def _relationships_info(self, top_k: int) -> None:
        tableprint.banner("Relationships")
        rows = [["Count", len(self.relationships)]]
        tableprint.table(rows)

        # k highly ranked relationships
        by_rank = self.relationships.sort_values("rank", ascending=False)[:top_k]

        # print 5 most connected entities
        tableprint.banner(f"{top_k} Top Ranked Relationships")
        tableprint.dataframe(by_rank[["source", "target", "rank"]])

    def _text_units_info(self) -> None:
        tableprint.banner("Text Units")
        rows = [["Count", len(self.text_units)]]
        tableprint.table(rows)

    def _community_info(self) -> None:
        tableprint.banner("Communities")

        levels = self.communities_reports["level"].unique()

        rows = []
        for level in levels:
            communities = self.communities_reports[
                self.communities_reports["level"] == level
            ]
            row = [level, len(communities)]
            rows.append(row)

        tableprint.table(rows, ["Level", "Number of Communities"])

    def report(
        self,
        top_k_entities: int = 5,
        top_k_relationships: int = 5,
    ) -> None:
        self._text_units_info()
        self._entity_info(top_k=top_k_entities)
        self._relationships_info(top_k=top_k_relationships)
        self._community_info()
