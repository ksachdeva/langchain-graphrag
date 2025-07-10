# Welcome to GraphRAG using langchain

**Transform your documents into searchable knowledge graphs**

## Overview

This library is an implementation of concepts from the paper:

[From Local to Global: A Graph RAG Approach to Query-Focused Summarization](https://arxiv.org/pdf/2404.16130)

Below excerpts are taken from the companion website of the paper:
[https://microsoft.github.io/graphrag/](https://microsoft.github.io/graphrag/)

GraphRAG is a structured, hierarchical approach to Retrieval Augmented Generation (RAG), as opposed to naive semantic-search approaches using plain text snippets. The GraphRAG process involves extracting a knowledge graph out of raw text, building a community hierarchy, generating summaries for these communities, and then leveraging these structures when performing RAG-based tasks.

There are two main phases in the GraphRAG process:

### Indexing

* Slice up an input corpus into a series of TextUnits, which act as analyzable units for the rest of the process, and provide fine-grained references in our outputs.

* Extract all entities, relationships, and key claims from the TextUnits using an LLM.

* Perform a hierarchical clustering of the graph using the Leiden technique. 

* Generate summaries of each community and its constituents from the bottom-up. This aids in holistic understanding of the dataset.

### Query

At query time, these structures are used to provide materials for the LLM context window when answering a question. The primary query modes are:

* Global Search for reasoning about holistic questions about the corpus by leveraging the community summaries.

* Local Search for reasoning about specific entities by fanning-out to their neighbors and associated concepts.

### Differences from the official implementation

There is an official implementation of the paper available at
[https://github.com/microsoft/graphrag](https://github.com/microsoft/graphrag)

The main differeneces are:

- Usage of [langchain](https://python.langchain.com/) as the foundation
- Support for LLMs and Embedding models other than the ones provided by Azure OpenAI
- Focus on modularity, readability, and extensibility
- Does not assume any workflow engine and leave it to the application

---

## Installation

```bash
pip install langchain-graphrag
```

## Documentation

### 1. **[Architecture Overview](architecture/overview.md)**
Understand how GraphRAG works and when to use Local vs Global search

### 2. **[Indexing Pipeline](guides/indexing_pipeline.md)**
How to build knowledge graphs from your documents with technical implementation details

### 3. **[Query System](guides/query_system.md)**
Local Search vs Global Search with practical examples

### 4. **[Data Flow & Examples](guides/data_flow_examples.md)**  
Real data transformations through each pipeline step with actual JSON examples

### 5. **[Advanced Examples](guides/graph_extraction/index.md)**
Jupyter notebooks for component-level customization and development