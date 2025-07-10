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

Make sure to rename `.env.example` to `.env` if you are using OpenAI or AzureOpenAI
and fill in the necessary environment variables.

#### Indexing 

```bash
# Step 1 - Index using convenient aliases
uv run poe simple-app-indexer-azure     # Uses Azure OpenAI
uv run poe simple-app-indexer-openai    # Uses OpenAI  
uv run poe simple-app-indexer-ollama    # Uses Ollama

# Or run the base command with custom parameters
uv run poe simple-app indexer index --input-file examples/input-data/book.txt --output-dir tmp --cache-dir tmp/cache --llm-type azure_openai --llm-model gpt-4o --embedding-type azure_openai --embedding-model text-embedding-3-large
```

```bash
# To see more options
$ uv run poe simple-app-indexer-help                 
Usage: main.py indexer index [OPTIONS]                                                                                            
                                                                                                                                   
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --input-file                                     FILE                          [default: None] [required]                    │
│ *  --output-dir                                     DIRECTORY                     [default: None] [required]                    │
│ *  --cache-dir                                      DIRECTORY                     [default: None] [required]                    │
│ *  --llm-type                                       [openai|azure_openai|ollama]  [default: None] [required]                    │
│ *  --llm-model                                      TEXT                          [default: None] [required]                    │
│ *  --embedding-type                                 [openai|azure_openai|ollama]  [default: None] [required]                    │
│ *  --embedding-model                                TEXT                          [default: None] [required]                    │
│    --chunk-size                                     INTEGER                       Chunk size for text splitting [default: 1200] │
│    --chunk-overlap                                  INTEGER                       Chunk overlap for text splitting              │
│                                                                                   [default: 100]                                │
│    --ollama-num-context                             INTEGER                       Context window size for ollama model          │
│                                                                                   [default: None]                               │
│    --enable-langsmith      --no-enable-langsmith                                  Enable Langsmith                              │
│                                                                                   [default: no-enable-langsmith]                │
│    --help                                                                         Show this message and exit.                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

#### Global Search

```bash
# Global search using provider-specific aliases (add --query "your question")
uv run poe simple-app-global-search-azure --query "What are the top themes in this story?"
uv run poe simple-app-global-search-openai --query "What are the top themes in this story?"
uv run poe simple-app-global-search-ollama --query "What are the top themes in this story?"

# Or use the base command for custom configurations
uv run poe simple-app-global-search --llm-type azure_openai --llm-model gpt-4o --query "What are the top themes in this story?"
```

```bash
$ uv run poe simple-app-query-help
$ uv run poe simple-app query global-search --help
Usage: main.py query global-search [OPTIONS]
                                                                                                                                            
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --output-dir                                     DIRECTORY                     [default: None] [required]                              │
│ *  --cache-dir                                      DIRECTORY                     [default: None] [required]                              │
│ *  --llm-type                                       [openai|azure_openai|ollama]  [default: None] [required]                              │
│ *  --llm-model                                      TEXT                          [default: None] [required]                              │
│ *  --query                                          TEXT                          [default: None] [required]                              │
│    --level                                          INTEGER                       Community level to search [default: 2]                  │
│    --ollama-num-context                             INTEGER                       Context window size for ollama model [default: None]    │
│    --enable-langsmith      --no-enable-langsmith                                  Enable Langsmith [default: no-enable-langsmith]         │
│    --help                                                                         Show this message and exit.                             │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

#### Local Search

```bash
# Local search using provider-specific aliases (add --query "your question")
uv run poe simple-app-local-search-azure --query "Who is Scrooge, and what are his main relationships?"
uv run poe simple-app-local-search-openai --query "Who is Scrooge, and what are his main relationships?"
uv run poe simple-app-local-search-ollama --query "Who is Scrooge, and what are his main relationships?"

# Or use the base command for custom configurations
uv run poe simple-app-local-search --llm-type azure_openai --llm-model gpt-4o --embedding-type azure_openai --embedding-model text-embedding-3-large --query "Who is Scrooge, and what are his main relationships?"
```

```bash
$ uv run poe simple-app query local-search --help
Usage: main.py query local-search [OPTIONS]                                                                                                 
                                                                                                                                             
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --output-dir                                     DIRECTORY                     [default: None] [required]                              │
│ *  --cache-dir                                      DIRECTORY                     [default: None] [required]                              │
│ *  --llm-type                                       [openai|azure_openai|ollama]  [default: None] [required]                              │
│ *  --llm-model                                      TEXT                          [default: None] [required]                              │
│ *  --query                                          TEXT                          [default: None] [required]                              │
│    --level                                          INTEGER                       Community level to search [default: 2]                  │
│ *  --embedding-type                                 [openai|azure_openai|ollama]  [default: None] [required]                              │
│ *  --embedding-model                                TEXT                          [default: None] [required]                              │
│    --ollama-num-context                             INTEGER                       Context window size for ollama model [default: None]    │
│    --enable-langsmith      --no-enable-langsmith                                  Enable Langsmith [default: no-enable-langsmith]         │
│    --help                                                                         Show this message and exit.                             │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

See `examples/simple-app/README.md` for more details.


### Available poe tasks

The project includes several convenient poe tasks (see `pyproject.toml` for complete list):

```bash
# Base command (for custom usage)
uv run poe simple-app               # Base: python examples/simple-app/app/main.py

# Help commands
uv run poe simple-app-help          # General help
uv run poe simple-app-indexer-help  # Indexer help  
uv run poe simple-app-query-help    # Query help

# Development
uv run poe test                     # Run tests
uv run poe lint                     # Check code quality
uv run poe format                   # Format code
uv run poe typecheck                # Type checking
uv run poe docs-serve               # Serve documentation locally

# Indexing (with preconfigured provider settings)
uv run poe simple-app-indexer-azure       # Index with Azure OpenAI
uv run poe simple-app-indexer-openai      # Index with OpenAI
uv run poe simple-app-indexer-ollama      # Index with Ollama
uv run poe simple-app-indexer             # Basic indexer (requires additional parameters)

# Reports
uv run poe simple-app-report              # Generate reports (requires prior indexing)

# Global search (add --query "your question")
uv run poe simple-app-global-search-azure --query "your question"   # Azure OpenAI
uv run poe simple-app-global-search-openai --query "your question"  # OpenAI
uv run poe simple-app-global-search-ollama --query "your question"  # Ollama
uv run poe simple-app-global-search --query "your question"         # Basic (needs provider params)

# Local search (add --query "your question") 
uv run poe simple-app-local-search-azure --query "your question"    # Azure OpenAI
uv run poe simple-app-local-search-openai --query "your question"   # OpenAI
uv run poe simple-app-local-search-ollama --query "your question"   # Ollama
uv run poe simple-app-local-search --query "your question"          # Basic (needs provider params)
```

### Development workflow

```bash
# 1. Setup
uv sync

# 2. Create a .env file (if not already present) and fill in your API keys and other configuration values.

# 3. Quick start with aliases
uv run poe simple-app-indexer-azure                                     # Index with Azure OpenAI
uv run poe simple-app-global-search-azure --query "What are the themes?" # Search with Azure OpenAI

# 4. Or try different providers
uv run poe simple-app-indexer-openai                                    # Index with OpenAI
uv run poe simple-app-local-search-openai --query "Who is the main character?" # Search with OpenAI

# 5. For custom configurations, use the base command
uv run poe simple-app indexer index --input-file your-file.txt --output-dir custom-output --llm-type azure_openai --llm-model gpt-4o

# 6. Development (optional)
uv run poe test && uv run poe lint     # Test and check code
```

## Roadmap / Things to do

The state of the library is far from complete. 

Here are some of the things that need to be done to make it more useful:

- [ ] Add more guides
- [ ] Document the APIs
- [ ] Add more tests