import logging
from dotenv import load_dotenv

from omegaconf import DictConfig, OmegaConf
import hydra


@hydra.main(version_base="1.3", config_path="./configs", config_name="indexing.yaml")
def indexer(cfg):

    # some how seeing httpx INFO LEVEL for requests
    # disabling it here for now.
    # TODO: should be able to do it via hydra config
    logger = logging.getLogger("httpx")
    logger.setLevel(logging.WARNING)

    load_dotenv()

    print(OmegaConf.to_yaml(cfg))
    indexer = hydra.utils.instantiate(cfg.indexer)
    indexer.run()


if __name__ == "__main__":
    indexer()
