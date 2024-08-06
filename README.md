# GraphRAG

** WORK IN PROGRESS **

This is an implementation of GraphRAG as described in 

https://arxiv.org/pdf/2404.16130

From Local to Global: A Graph RAG Approach to Query-Focused Summarization

Official implementation by the authors of the paper is available at:

https://github.com/microsoft/graphrag/

## Why re-implementation 🤔?

The primary reasons for re-implementing:

* Develop better understanding of the intricacies of the paper by implementing it
* Official implementation
    - is not built upon popular frameworks like langchain, llamaIndex etc
    - is bit difficult to understand because of reliance on `datashaper` package
    - does not support models other than OpenAI or AzureOpenAI

## Install (Not Recommended yet!)

Note - this is work in progress so installing the package is not recommended yet.
It would be better to clone the repo and try out current state of the code. 
See below for more details.

I published the package so as to reserve the name. Clone the repo and install the package locally.

```bash
pip install langchain-graphrag
```

## Projects 

There are 3 projects in the repo:

### `langchain_graphrag` 

This is the core library that implements the GraphRAG paper. It is built on top of the `langchain` library.

The concepts described in GraphRAG paper are implemented in a modular fashion with easy extensibility and replacement in mind. 

To use the development version (Recommended as it is under active development):

#### Clone the repo

```bash
git clone https://github.com/ksachdeva/langchain-graphrag.git
```
#### Open in VSCode devcontainer (Recommended)

Devcontainer will install all the dependencies

#### If not using devcontainer

Make sure you have `rye` installed. See https://rye.astral.sh/

```bash
# sync all the dependencies
rye sync
```

### `examples/simple-app`

This is a simple `typer` based CLI app.

In terms of configuration it is limited by the number of command line options exposed.

```bash
# To generate the index
# default set azure_openai/gpt4-o/text-embedding-3-small
# you can change the model and other parameters from command line 
rye run simple-app-indexer --help
```

See `examples/simple-app/README.md` for more details.

### `examples/sophisticated-app`

This is a `hydra` (https://hydra.cc/) based app. 

I chose `hydra` so that I can easily experiment with different configurations for e.g. different tokenizers, llms, community detection algorithms etc.

There is not much code in the app itself as the entire orchestration is done with the help of hydra configuration. 

```bash
# To generate the index
# possible experiment values (see examples/sophisticated-app/app/configs/experiment):
# azure_openai_gpt4o
# openai_gpt4mini
# gemma2_9b (via ollama)
# gemma2_27b (via ollama)

rye run sophisticated-app-indexer indexing/experiment=openai_gpt4mini
```

See `examples/sophisticated-app/README.md` for more details.