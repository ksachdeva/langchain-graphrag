from typing import cast

import pandas as pd
from langchain_core.vectorstores import VectorStore
from pandas._typing import Suffixes
from tqdm import tqdm


def _array_agg_distinct(series: pd.Series) -> list[pd.Series]:
    return list(series.unique())


def _make_temporary_frame(
    entities_or_relationships: pd.DataFrame,
    rename_id_to: str,
) -> pd.DataFrame:
    # select only id & text_unit_ids columns
    tmp = entities_or_relationships[["id", "text_unit_ids"]]

    # flatten the text_unit_ids
    tmp = tmp.explode("text_unit_ids")

    # group by text_unit_ids
    grouped = tmp.groupby("text_unit_ids", sort=False)

    aggregations = {"id": _array_agg_distinct}

    output = cast(pd.DataFrame, grouped.agg(aggregations))
    output.rename(columns={"id": rename_id_to}, inplace=True)

    return output.reset_index()


class TextUnitsTableGenerator:
    def __init__(self, vector_store: VectorStore):
        self._vector_store = vector_store

    def run(
        self,
        base_text_units: pd.DataFrame,
        entities: pd.DataFrame,
        relationships: pd.DataFrame,
    ) -> pd.DataFrame:
        entities_df = _make_temporary_frame(
            entities,
            rename_id_to="entity_ids",
        )
        entities_df.rename(columns={"text_unit_ids": "id"}, inplace=True)

        relationships_df = _make_temporary_frame(
            relationships,
            rename_id_to="relationship_ids",
        )
        relationships_df.rename(columns={"text_unit_ids": "id"}, inplace=True)

        text_units_entities = base_text_units.merge(
            entities_df,
            left_on="id",
            right_on="id",
            how="left",
            suffixes=cast(Suffixes, ["_1", "_2"]),
            indicator=True,
        )

        text_units_entities = base_text_units.merge(
            entities_df,
            left_on="id",
            right_on="id",
            how="left",
            suffixes=cast(Suffixes, ["_1", "_2"]),
            indicator=True,
        ).drop("_merge", axis=1)

        text_units = text_units_entities.merge(
            relationships_df,
            left_on="id",
            right_on="id",
            how="left",
            suffixes=cast(Suffixes, ["_1", "_2"]),
            indicator=True,
        ).drop("_merge", axis=1)

        def _run_embedder(series: pd.Series) -> None:
            chunk_to_embedd = series["text"]
            chunk_id = series["id"]
            chunk_metadata = dict(document_id=series["document_id"])

            self._vector_store.add_texts(
                [chunk_to_embedd],
                metadata=[chunk_metadata],
                ids=[chunk_id],
            )

        tqdm.pandas(desc="Generating chunk embedding ...")
        text_units.progress_apply(
            _run_embedder,
            axis=1,
        )

        return text_units
