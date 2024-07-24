from langchain_core.document_loaders.base import BaseLoader


from omegaconf import DictConfig, OmegaConf
import hydra


@hydra.main(version_base="1.3", config_path="./configs", config_name="indexing.yaml")
def indexer(cfg):
    print(OmegaConf.to_yaml(cfg))
    indexer = hydra.utils.instantiate(cfg.indexer)
    indexer.run()


if __name__ == "__main__":
    indexer()
