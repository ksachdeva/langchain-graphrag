import itertools
import pandas as pd


def _find_in_network_relationships(
    df_entities: pd.DataFrame,
    df_relationships: pd.DataFrame,
):
    entities_ids = df_entities["id"].tolist()
    entities_pairs = itertools.combinations(entities_ids, 2)

    # print(entities_ids)

    def filter_in_network_relationships(source_id: str, target_id: str) -> bool:
        for pair in entities_pairs:
            if (source_id == pair[0]) and (target_id == pair[1]):
                print("Match1")
                return True
            if (source_id == pair[1]) and (target_id == pair[0]):
                print("Match2")
                return True

        return False

    # print(list(entities_pairs))

    df_relationships["is_in_network"] = df_relationships.apply(
        lambda x: filter_in_network_relationships(x.source_id, x.target_id),
        axis=1,
    )

    how_many = (df_relationships["is_in_network"] == True).sum()

    # print(how_many)
    # print(entities_ids)
    # print(df_relationships[["source_id", "target_id"]])

    # df_in_network_relationships = df_relationships[

    # ]

    # print(df_in_network_relationships)

    return df_relationships


class RelationshipsSelector:
    def run(
        self,
        df_entities: pd.DataFrame,
        df_relationships: pd.DataFrame,
    ) -> pd.DataFrame:
        in_network_relationships = _find_in_network_relationships(
            df_entities,
            df_relationships,
        )
