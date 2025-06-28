# GraphRAG Architecture Overview

GraphRAG processes document collections into structured knowledge graphs. The system supports both entity-specific queries and thematic analysis queries.

---

## Core System Overview

GraphRAG operates through **two fundamental processes**:

| Phase | Purpose | Output |
|-------|---------|--------|
| **Indexing Pipeline** | Analyzes documents to construct structured knowledge | Knowledge Graph + Community Reports |
| **Query Engine** | Uses knowledge graph for contextual responses | Contextual Answers |

```mermaid
flowchart LR
    A["Document Collection"] --> B["Indexing Pipeline"]
    B --> C["Knowledge Graph<br/>+ Community Reports"]
    C --> D["Query Engine"]
    D --> E["Contextual Responses"]
    
    classDef inputStyle fill:#f8f9fa,stroke:#6c757d,stroke-width:2px,color:#212529
    classDef processStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#0d47a1
    classDef dataStyle fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
    classDef outputStyle fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    
    class A inputStyle
    class B,D processStyle
    class C dataStyle
    class E outputStyle
```

## Indexing Pipeline Architecture

The indexing process turns raw documents into organized knowledge through a step-by-step process:

```mermaid
flowchart TD
    subgraph input ["Input Processing"]
        A["Raw Documents"]
        B["Document Splitting"]
        A --> B
    end
    
    subgraph extraction ["Knowledge Extraction"]
        C["Entity Recognition"]
        D["Relationship Mining"]
        E["Graph Construction"]
        C --> E
        D --> E
    end
    
    subgraph organization ["Knowledge Organization"]
        F["Community Detection"]
        G["Summary Generation"]
        F --> G
    end
    
    subgraph output ["Query Artifacts"]
        H["Searchable Knowledge Base"]
    end
    
    B --> C
    B --> D
    E --> F
    G --> H
    
    classDef inputClass fill:#f8f9fa,stroke:#6c757d,stroke-width:2px
    classDef processClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef organizeClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef outputClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    
    class A,B inputClass
    class C,D,E processClass
    class F,G organizeClass
    class H outputClass
```

---

## Practical Example

> **Input Document**: "Ratan Tata served as Chairman of Tata Group from 1991 to 2012, transforming it into a global business group with acquisitions like Jaguar Land Rover."

### GraphRAG Knowledge Extraction

| Extract Type | Results |
|--------------|---------|
| **Entities** | Ratan Tata • Tata Group • Jaguar Land Rover • 1991 • 2012 |
| **Relationships** | Ratan Tata → served_as_chairman → Tata Group<br/>Tata Group → acquired → Jaguar Land Rover |
| **Communities** | Business Leadership • Automotive Industry |

---

## Query Engine Architecture

GraphRAG uses **two different search methods** to handle different types of questions:

### Local Search (Entity-Focused Queries)

| Aspect | Details |
|--------|---------|
| **Best For** | Specific factual questions about entities and relationships |
| **Examples** | "What companies did Ratan Tata lead?" • "When did Tata acquire Jaguar?" |
| **How it Works** | Finds entities → Follows connections → Builds context |
| **Characteristics** | High precision with specific responses |

### Global Search (Thematic Analysis)

| Aspect | Details |
|--------|---------|
| **Best For** | Big-picture questions requiring complete insights |
| **Examples** | "Key business transformation strategies?" • "Leadership patterns in business groups?" |
| **How it Works** | Community analysis → Pre-built summaries → Insight combining |
| **Characteristics** | Complete coverage with synthesized insights |

```mermaid
flowchart TD
    A["User Query"] --> B{"Query Classification"}
    
    subgraph local ["Local Search Pipeline"]
        C["Entity Resolution"]
        D["Graph Traversal"]
        E["Context Assembly"]
        C --> D --> E
    end
    
    subgraph global ["Global Search Pipeline"]
        F["Community Matching"]
        G["Report Synthesis"]
        H["Insight Aggregation"]
        F --> G --> H
    end
    
    I["Response Generation"]
    
    B -->|"Entity-Specific"| local
    B -->|"Thematic"| global
    E --> I
    H --> I
    
    classDef queryStyle fill:#f8f9fa,stroke:#6c757d,stroke-width:2px,color:#212529
    classDef decisionStyle fill:#fff3e0,stroke:#f57c00,stroke-width:3px,color:#e65100
    classDef localStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#0d47a1
    classDef globalStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef outputStyle fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    
    class A queryStyle
    class B decisionStyle
    class C,D,E localStyle
    class F,G,H globalStyle
    class I outputStyle
```

---

## Comparison with Traditional Search

| Aspect | Traditional Search | GraphRAG |
|-----------|------------------|----------|
| **Understanding** | Keyword matching only | Meaningful connections & relationships |
| **Analysis Depth** | Single-level results | **Detailed** (Local) + **Strategic** (Global) insights |
| **Source Tracking** | Basic page references | Complete traceability to original documents |
| **Context Awareness** | Isolated results | Connected knowledge with relationships |

---

## Knowledge Architecture Components

GraphRAG organizes information into **four interconnected layers**:

| Component | Description | Example |
|-----------|-------------|---------|
| **Entities** | People, organizations, and concepts | `Ratan Tata` • `Tata Group` • `Jaguar Land Rover` |
| **Relationships** | How different entities connect to each other | `Ratan Tata served as Chairman of Tata Group` |
| **Communities** | Groups of related entities by topic | `Business Leadership` • `Automotive Industry` |
| **Text Units** | Original text pieces with entity links | `"Ratan Tata served as Chairman of Tata Group from 1991..."` |

---

## Query Strategy Selection Guide

**Choose the right search method for your question type:**

| Query Example | Search Strategy | Why This Choice |
|---------------|-----------------|-----------------|
| `"What is Ratan Tata's background?"` | **Local Search** | Entity-specific biographical information |
| `"Which companies did Tata Group acquire?"` | **Local Search** | Specific relationship and timeline queries |
| `"What are the main business transformation patterns?"` | **Global Search** | Theme analysis across multiple entities |
| `"Analyze the strategic evolution of Indian business groups"` | **Global Search** | Complete pattern recognition and insights |

---

## Implementation Resources

| Resource | Description | Best For |
|----------|-------------|----------|
| **[Indexing Pipeline Guide](../guides/indexing_pipeline.md)** | Complete indexing process documentation | Understanding the build process |
| **[Query System Guide](../guides/query_system.md)** | Local vs Global search explained | Learning when to use each query type |
| **[System Customization Guide](../guides/customization.md)** | Component configuration and extensions | Adapting to your needs |

---

## Key Value Proposition

> **GraphRAG transforms how you work with documents** by building intelligent knowledge structures that understand context and relationships. This enables both **precise factual questions** and **strategic analytical insights** - going far beyond traditional search.

---

## Related Documentation

**[Indexing Pipeline](../guides/indexing_pipeline.md)**  
Technical implementation details and configuration options for building knowledge graphs.

**[Documentation Index](../index.md)**  
Return to documentation overview 