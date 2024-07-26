# A hydra configuration based app

The purpose of this app is to use `hydra` to easily experiment with different
configurations for e.g. different tokenizers, llms, community detection algorithms etc.

## Install

```bash
pip install -r requirements.txt
```

## Run

Make sure the `langchain_graphrag` in your PYTHONPATH

### Using Azure OpenAI or OpenAI

- See .env.example for the environment variables that need to be set.
- Rename .env.example to .env

```bash
# run using azure openai
python examples/sophisticated-app/app/main.py experiment=azure_openai_gpt4o
```

### Using Ollama

```bash
# This command will use gemma2:9b-instruct-q8_0
python examples/sophisticated-app/app/main.py experiment=gemma2_9b
```

Look in the `examples/sophisticated-app/app/configs/experiment/gemma2_9b.yaml` 

If you want to use a different model here are few different ways to do it:

#### Approach 1:

Create a config file in the `examples/sophisticated-app/app/configs/experiment` folder.

#### Approach 2:

Hydra allows you to override config from command line. 

Here is an example of how you could override the few parameters

```bash
python examples/sophisticated-app/app/main.py experiment=gemma2_27b indexer.er_extractor.llm.base_url=http://rog-extreme:11434 indexer.er_extractor.llm.model=gemma2:27b-instruct-q8_0
```