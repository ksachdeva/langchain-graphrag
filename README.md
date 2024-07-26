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

## Will it be released as pip installable package?

Perhaps!

## Projects 

There are 3 projects in the repo:

### `langchain_graphrag` 

This is the core library that implements the GraphRAG paper. It is built on top of the `langchain` library.

The concepts described in GraphRAG paper are implemented in a modular fashion with easy extensibility and replacement in mind. 

### `examples/simple-app`

This is a simple `typer` based CLI app.

In terms of configuration it is limited by the number of command line options exposed.

See `examples/simple-app/README.md` for more details.

### `examples/sophisticated-app`

This is a `hydra` based app. 

I chose `hydra` so that I can easily experiment with different configurations for e.g. different tokenizers, llms, community detection algorithms etc.

There is not much code in the app itself as the entire orchestration is done with the help of hydra configuration. 

See `examples/sophisticated-app/README.md` for more details.