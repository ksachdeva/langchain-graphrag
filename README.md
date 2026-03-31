# GraphRAG - Powered by LangChain

[![Documentation build status](https://readthedocs.org/projects/langchain-graphrag/badge/?version=latest
)](https://langchain-graphrag.readthedocs.io/en/latest/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

---

This is an implementation of GraphRAG as described in

https://arxiv.org/pdf/2404.16130

From Local to Global: A Graph RAG Approach to Query-Focused Summarization

Official implementation by the authors of the paper is available at:

https://github.com/microsoft/graphrag/


## Guides

- [Text Unit Extraction](https://langchain-graphrag.readthedocs.io/en/latest/guides/text_units_extraction/)
- [Graph Extraction](https://langchain-graphrag.readthedocs.io/en/latest/guides/graph_extraction/)

## Why re-implementation 🤔?

### Personal Preference

While I generally prefer utilizing and refining existing implementations, as re-implementation often isn't optimal, I decided to take a different approach after encountering several challenges with the official version.

### Issues with the Official Implementation

- Lacks integration with popular frameworks like LangChain, LlamaIndex, etc.
- Limited to OpenAI and AzureOpenAI models, with no support for other providers.

### Why rely on established frameworks like LangChain?

Using an established foundation like LangChain offers numerous benefits. It abstracts various providers, whether related to LLMs, embeddings, vector stores, etc., allowing for easy component swapping without altering core logic or adding complex support. More importantly, a solid foundation like this lets you focus on the problem's core logic rather than reinventing the wheel.

LangChain also supports advanced features like batching and streaming, provided your components align with the framework’s guidelines. For instance, using chains (LCEL) allows you to take full advantage of these capabilities.

### Modularity & Extensibility-focused design

The APIs are designed to be modular and extensible. You can replace any component with your own implementation as long as it implements the required interface. 

Given the nature of the domain, this is important for conducting experiments by swapping out various components.

## Install 

```bash
pip install langchain-graphrag
```

## Projects

There are 2 projects in the repo:

### `langchain_graphrag`

This is the core library that implements the GraphRAG paper. It is built on top of the `langchain` library.

#### An example code for local search using the API

Below is a snippet taken from the `simple-app` to show the style of API
and extensibility offered by the library.

Almost all the components (classes/functions) can be replaced by your own
implementations. The library is designed to be modular and extensible.

```python
# Reload the vector Store that stores
# the entity name & description embeddings
entities_vector_store = ChromaVectorStore(
    collection_name="entity_name_description",
    persist_directory=str(vector_store_dir),
    embedding_function=make_embedding_instance(
        embedding_type=embedding_type,
        model=embedding_model,
        cache_dir=cache_dir,
    ),
)

# Build the Context Selector using the default
# components; You can supply the various components
# and achieve as much extensibility as you want
# Below builds the one using default components.
context_selector = ContextSelector.build_default(
    entities_vector_store=entities_vector_store,
    entities_top_k=10,
    community_level=cast(CommunityLevel, level),
)

# Context Builder is responsible for taking the
# result of Context Selector & building the
# actual context to be inserted into the prompt
# Keeping these two separate further increases
# extensibility & maintainability
context_builder = ContextBuilder.build_default(
    token_counter=TiktokenCounter(),
)

# load the artifacts
artifacts = load_artifacts(artifacts_dir)

# Make a langchain retriever that relies on
# context selection & builder
retriever = LocalSearchRetriever(
    context_selector=context_selector,
    context_builder=context_builder,
    artifacts=artifacts,
)

# Build the LocalSearch object
local_search = LocalSearch(
    prompt_builder=LocalSearchPromptBuilder(),
    llm=make_llm_instance(llm_type, llm_model, cache_dir),
    retriever=retriever,
)

# it's a callable that returns the chain
search_chain = local_search()

# you could invoke
# print(search_chain.invoke(query))

# or, you could stream
for chunk in search_chain.stream(query):
    print(chunk, end="", flush=True)
```


#### Clone the repo

```bash
git clone https://github.com/ksachdeva/langchain-graphrag.git
```
#### Open in VSCode devcontainer (Recommended)

Devcontainer will install all the dependencies

#### If not using devcontainer


1. **Clone the repository**

```bash
git clone https://github.com/ksachdeva/langchain-graphrag.git
cd langchain-graphrag
```

2. **Install dependencies (requires Python 3.10+ and [uv](https://github.com/astral-sh/uv))**

### Installation

You can install `uv` using the standalone installers or from PyPI:

#### Standalone installers

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### From PyPI

```bash
# With pip
pip install uv

# Or pipx
pipx install uv
```

If installed via the standalone installer, you can update `uv` to the latest version:

```bash
uv self update
```

### Setting up the environment and dependencies installation

```bash
uv sync
```

### `examples/simple-app`

This is a simple `typer` based CLI app.

In terms of configuration it is limited by the number of command line options exposed.

That said, the way core library is written you can easily replace any component by
your own implementation i.e. your choice of LLM, embedding models etc. Even some of
the classes as long as they implement the required interface.

**Note**:

Copy `examples/simple-app/.env.example` to `examples/simple-app/.env` and fill in your API keys and provider settings.

```bash
cp examples/simple-app/.env.example examples/simple-app/.env
```

Edit `examples/simple-app/.env` to choose your provider and set API keys:

```bash
# Provider — pick one: openai | azure_openai | ollama
LLM_TYPE=openai
LLM_MODEL=gpt-4o
EMBEDDING_TYPE=openai
EMBEDDING_MODEL=text-embedding-3-small
```

#### Indexing 

```bash
# Index using the provider configured in .env
uv run poe index

# To see all indexer options
uv run poe indexer-help
```

#### Global Search

```bash
uv run poe global-search --query "What are the top themes in this story?"

# To see all options
uv run poe query-help
```

#### Local Search

```bash
uv run poe local-search --query "Who is Scrooge, and what are his main relationships?"
```

See `examples/simple-app/README.md` for more details.


### Available poe tasks

The project includes several convenient poe tasks (see `poe.toml` for complete list):

```bash
# App commands
uv run poe app-help           # General help
uv run poe indexer-help       # Indexer help
uv run poe query-help         # Query help

# Run (provider configured via examples/simple-app/.env)
uv run poe index              # Index input data
uv run poe report             # Generate reports (requires prior indexing)
uv run poe global-search --query "your question"
uv run poe local-search --query "your question"

# Development
uv run poe test               # Run tests
uv run poe lint               # Check code quality
uv run poe format             # Format code
uv run poe typecheck          # Type checking
uv run poe docs-serve         # Serve documentation locally
```

### Development workflow

```bash
# 1. Setup
uv sync

# 2. Configure provider and API keys
cp examples/simple-app/.env.example examples/simple-app/.env
# Edit examples/simple-app/.env — fill in API keys, set LLM_TYPE

# 3. Index and search
uv run poe index
uv run poe global-search --query "What are the themes?"
uv run poe local-search --query "Who is the main character?"

# 4. Development (optional)
uv run poe test && uv run poe lint     # Test and check code
```

## Roadmap / Things to do

The state of the library is far from complete. 

Here are some of the things that need to be done to make it more useful:

- [ ] Add more guides
- [ ] Document the APIs
- [ ] Add more tests