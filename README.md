# GraphRAG

** WORK IN PROGRESS **

This is an implementation of GraphRAG as described in 

https://arxiv.org/pdf/2404.16130

From Local to Global: A Graph RAG Approach to Query-Focused Summarization

Official implementation by the authors of the paper is available at:

https://github.com/microsoft/graphrag/

## Why re-implementation 🤔?

The primary reasons for me re-implementing this are:

* Explore/Learn/Discover the intricacies of the paper by implementing it
* Official implementation
    - is not built upon popular frameworks like langchain, llamaIndex etc
    - is bit difficult to understand because of reliance on `datashaper` package
    - does not support models other than OpenAI or AzureOpenAI

## Will it be released as pip installable package?

Perhaps!

## Main projects

There are two projects in the repo:

### `langchain_graphrag` 

This is the core library that implements the GraphRAG paper. It is built on top of `langchain` library.

The components/phases described in GraphRAG paper as implemented as modular classes that can be composed
to perform the indexing and query tasks.

### `examples/app`

This is a `hydra` based app. 

I chose `hydra` so that I can easily experiment with different configurations for e.g. different tokenizers, llms, community detection algorithms etc.

There is not much code in the app itself as the entire orchestration is done with the help of hydra configuration. 

## How can I run it?

Make sure to open the repo in `devcontainer` in VSCode.

```bash
# install dependencies
pip install -r requirements.txt
pip install -r examples/requirements_app.txt
```

### Using Azure OpenAI or OpenAI

- See examples/.env.example for the environment variables that need to be set.
- Rename .env.example to .env

```bash
# run using azure openai
python examples/app/main.py experiment=azure_openai_gpt4o
```

### Using Ollama

```bash
# This command will use gemma2:9b-instruct-q8_0
python examples/app/main.py experiment=gemma2_9b
```

Look in the `examples/app/configs/experiment/gemma2_9b.yaml` 

If you want to use a different model here are few different ways to do it:

#### Approach 1:

Create a config file in the `examples/app/configs/experiment` folder.

#### Approach 2:

Hydra allows you to override config from command line. 

Here is an example of how you could override the few parameters

```bash
python examples/app/main.py experiment=gemma2_27b indexer.er_extractor.llm.base_url=http://rog-extreme:11434 indexer.er_extractor.llm.model=gemma2:27b-instruct-q8_0
```