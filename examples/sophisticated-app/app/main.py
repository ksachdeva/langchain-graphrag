import logging
from dotenv import load_dotenv

from omegaconf import DictConfig, OmegaConf
import hydra

from langchain_community.storage import SQLStore
from langchain.embeddings.cache import CacheBackedEmbeddings


@hydra.main(version_base="1.3", config_path="./configs", config_name="indexing.yaml")
def indexer(cfg):

    # some how seeing httpx INFO LEVEL for requests
    # disabling it here for now.
    # TODO: should be able to do it via hydra config
    for logger_name in ["httpx", "gensim"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)

    load_dotenv()

    print(OmegaConf.to_yaml(cfg))

    underlying_embedding_model = hydra.utils.instantiate(cfg.embedding_model)

    # hack: to create the table for embedding store
    embedding_db_path = cfg.paths.sqllite_embedding_cache_dir + "/embedding.db"
    store = SQLStore(
        namespace=underlying_embedding_model.model,
        db_url=embedding_db_path,
    )
    store.create_schema()

    cached_embedding_model = CacheBackedEmbeddings.from_bytes_store(
        underlying_embeddings=underlying_embedding_model,
        document_embedding_cache=store,
    )

    entity_embedding_generator = hydra.utils.instantiate(
        cfg.indexing.entity_embedding,
        embedding_model=cached_embedding_model,
    )

    relationship_embedding_generator = hydra.utils.instantiate(
        cfg.indexing.relationship_embedding,
        embedding_model=cached_embedding_model,
    )

    indexer = hydra.utils.instantiate(
        cfg.indexing.indexer,
        entities_table_generator={
            "entity_embedding_generator": entity_embedding_generator
        },
        relationships_table_generator={
            "relationship_embedding_generator": relationship_embedding_generator
        },
        text_units_table_generator={"embedding_model": cached_embedding_model},
    )
    indexer.run()


if __name__ == "__main__":
    indexer()
