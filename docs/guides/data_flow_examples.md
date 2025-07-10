# Data Flow & Examples Guide

This guide demonstrates how documents are transformed through each step of the GraphRAG pipeline, using real-world data examples.

---

## Pipeline Overview

The GraphRAG pipeline transforms unstructured documents into a queryable knowledge graph through 8 systematic steps:

1. **Raw Document Input** → Document ingestion and preparation
2. **Text Unit Extraction** → Chunking into analyzable segments
3. **Entity Extraction** → LLM identification of key concepts
4. **Relationship Extraction** → LLM mapping of entity connections
5. **Knowledge Graph Construction** → Building connected network
6. **Community Detection** → Clustering related entities
7. **Community Report Generation** → LLM summarization of themes
8. **Final Artifacts Generation** → Query-optimized data structures

---

## Step 1: Raw Document Input

### Sample Input Document

**File: `business_leadership.txt`**
```
Indian Business Leadership Patterns

Successful Indian business leaders demonstrate unique characteristics that blend traditional values with modern business practices. Leaders like Ratan Tata, N.R. Narayana Murthy, and Azim Premji share common traits of long-term thinking and social responsibility.

These leaders prioritize stakeholder capitalism over shareholder primacy, investing heavily in employee development, community welfare, and sustainable business practices. Their approach to international expansion combines global ambitions with deep respect for local cultures and practices.

Innovation leadership in Indian companies often focuses on frugal innovation - creating high-quality solutions at affordable prices. This approach has enabled Indian companies to serve both domestic and international markets effectively.
```

**Document Properties:**
- **Length**: 847 characters
- **Word Count**: ~120 words  
- **Format**: Plain text
- **Content Type**: Business analysis

---

## Step 2: Text Unit Extraction

The document gets split into analyzable chunks with metadata.

### Generated Text Units

**Text Unit 1:**
```json
{
  "id": "uuid-text-unit-001",
  "document_id": "uuid-doc-001",
  "text_unit": "Indian Business Leadership Patterns\n\nSuccessful Indian business leaders demonstrate unique characteristics that blend traditional values with modern business practices. Leaders like Ratan Tata, N.R. Narayana Murthy, and Azim Premji share common traits of long-term thinking and social responsibility."
}
```

**Text Unit 2:**
```json
{
  "id": "uuid-text-unit-002", 
  "document_id": "uuid-doc-001",
  "text_unit": "These leaders prioritize stakeholder capitalism over shareholder primacy, investing heavily in employee development, community welfare, and sustainable business practices. Their approach to international expansion combines global ambitions with deep respect for local cultures and practices."
}
```

**Text Unit 3:**
```json
{
  "id": "uuid-text-unit-003",
  "document_id": "uuid-doc-001", 
  "text_unit": "Innovation leadership in Indian companies often focuses on frugal innovation - creating high-quality solutions at affordable prices. This approach has enabled Indian companies to serve both domestic and international markets effectively."
}
```

### Key Transformations
- **Single document** → **3 text units**
- **Maintains source traceability** via document reference
- **Adds unique identifiers** for each text unit
- **Adds metadata** for downstream processing

---

## Step 3: Entity Extraction

The LLM identifies people, organizations, and concepts from each text unit.

### Extracted Entities

**From Text Unit 1:**
```json
[
  {
    "id": "uuid-entity-001",
    "title": "Ratan Tata",
    "type": "PERSON", 
    "description": "Prominent Indian business leader known for long-term thinking and social responsibility",
    "text_unit_ids": ["uuid-text-unit-001"]
  },
  {
    "id": "uuid-entity-002", 
    "title": "N.R. Narayana Murthy",
    "type": "PERSON",
    "description": "Indian business leader demonstrating traditional values with modern practices",
    "text_unit_ids": ["uuid-text-unit-001"]
  },
  {
    "id": "uuid-entity-003",
    "title": "Azim Premji", 
    "type": "PERSON",
    "description": "Indian business leader sharing traits of long-term thinking and social responsibility",
    "text_unit_ids": ["uuid-text-unit-001"]
  },
  {
    "id": "uuid-entity-004",
    "title": "Indian Business Leadership",
    "type": "CONCEPT",
    "description": "Leadership approach blending traditional values with modern business practices",
    "text_unit_ids": ["uuid-text-unit-001"]
  }
]
```

**From Text Unit 2:**
```json
[
  {
    "id": "uuid-entity-005",
    "title": "Stakeholder Capitalism",
    "type": "CONCEPT", 
    "description": "Business approach prioritizing multiple stakeholders over shareholders only",
    "text_unit_ids": ["uuid-text-unit-002"]
  },
  {
    "id": "uuid-entity-006",
    "title": "International Expansion",
    "type": "CONCEPT",
    "description": "Global business growth strategy combining ambitions with cultural respect",
    "text_unit_ids": ["uuid-text-unit-002"]
  }
]
```

### Entity Summary
- **Total Entities**: 6
- **People**: 3 (Ratan Tata, N.R. Narayana Murthy, Azim Premji)
- **Concepts**: 3 (Leadership patterns, Stakeholder Capitalism, etc.)
- **Traceability**: Each entity links back to source text units

---

## Step 4: Relationship Extraction

The LLM identifies how entities connect to each other.

### Extracted Relationships

```json
[
  {
    "id": "uuid-rel-001",
    "source": "Ratan Tata",
    "target": "Indian Business Leadership", 
    "description": "Ratan Tata exemplifies Indian business leadership patterns",
    "rank": 6,
    "text_unit_ids": ["uuid-text-unit-001"]
  },
  {
    "id": "uuid-rel-002", 
    "source": "N.R. Narayana Murthy",
    "target": "Indian Business Leadership",
    "description": "N.R. Narayana Murthy demonstrates Indian business leadership characteristics",
    "rank": 6,
    "text_unit_ids": ["uuid-text-unit-001"]
  },
  {
    "id": "uuid-rel-003",
    "source": "Azim Premji", 
    "target": "Indian Business Leadership",
    "description": "Azim Premji shares common Indian business leadership traits", 
    "rank": 6,
    "text_unit_ids": ["uuid-text-unit-001"]
  },
  {
    "id": "uuid-rel-004",
    "source": "Indian Business Leadership",
    "target": "Stakeholder Capitalism",
    "description": "Indian business leaders prioritize stakeholder capitalism approach",
    "rank": 5, 
    "text_unit_ids": ["uuid-text-unit-002"]
  },
  {
    "id": "uuid-rel-005",
    "source": "Indian Business Leadership", 
    "target": "International Expansion",
    "description": "Indian leaders approach international expansion with cultural respect",
    "rank": 5,
    "text_unit_ids": ["uuid-text-unit-002"]
  }
]
```

### Relationship Patterns
- **Hub Entity**: "Indian Business Leadership" connects to most others
- **Rank Scores**: Indicate relationship importance (sum of source + target degrees)
- **Directional**: Source → Target relationships
- **Traceable**: Links back to source text units

---

## Step 5: Knowledge Graph Construction

Entities and relationships combine into a unified graph structure.

### Graph Representation

```mermaid
graph TD
    A["Ratan Tata<br/>PERSON"] --> B["Indian Business Leadership<br/>CONCEPT"]
    C["N.R. Narayana Murthy<br/>PERSON"] --> B
    D["Azim Premji<br/>PERSON"] --> B
    B --> E["Stakeholder Capitalism<br/>CONCEPT"]
    B --> F["International Expansion<br/>CONCEPT"]
    B --> G["Frugal Innovation<br/>CONCEPT"]
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style C fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style D fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style B fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style E fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style F fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style G fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

### Graph Statistics
- **Nodes**: 6 entities
- **Edges**: 5 relationships  
- **Connected Components**: 1 (fully connected)
- **Hub Nodes**: "Indian Business Leadership" (degree: 3)

---

## Step 6: Community Detection

The system groups related entities into communities using graph clustering.

### Detected Communities

**Community 1: Business Leadership**
```json
{
  "id": 1,
  "nodes": [
    {
      "name": "Ratan Tata",
      "parent_cluster": null,
      "is_final_cluster": true
    },
    {
      "name": "N.R. Narayana Murthy",
      "parent_cluster": null,
      "is_final_cluster": true
    },
    {
      "name": "Azim Premji",
      "parent_cluster": null,
      "is_final_cluster": true
    },
    {
      "name": "Indian Business Leadership",
      "parent_cluster": null,
      "is_final_cluster": true
    }
  ]
}
```

**Community 2: Business Practices** 
```json
{
  "id": 2,
  "nodes": [
    {
      "name": "Stakeholder Capitalism",
      "parent_cluster": null,
      "is_final_cluster": true
    },
    {
      "name": "International Expansion",
      "parent_cluster": null,
      "is_final_cluster": true
    },
    {
      "name": "Frugal Innovation",
      "parent_cluster": null,
      "is_final_cluster": true
    }
  ]
}
```

### Community Analysis
- **2 communities** detected at level 0
- **Node-based grouping**: Community nodes represent entities with clustering metadata
- **Logical grouping**: People vs Concepts naturally separated through graph structure

---

## Step 7: Community Report Generation

Each community gets a comprehensive summary report.

### Generated Community Reports

**Community 1 Report:**
```markdown
# Indian Business Leadership Community

## Summary
This community centers around prominent Indian business leaders who have shaped modern business practices in India. The core figures - Ratan Tata, N.R. Narayana Murthy, and Azim Premji - represent a distinctive leadership philosophy that blends traditional Indian values with contemporary business strategies.

## Key Characteristics
- **Long-term Vision**: Focus on sustainable growth over short-term gains
- **Social Responsibility**: Integration of community welfare into business strategy  
- **Value Integration**: Blending traditional ethics with modern practices
- **Institutional Building**: Emphasis on creating lasting organizational capabilities

## Relationships
The leaders in this community are connected through shared leadership philosophies and approaches to business management, demonstrating consistent patterns across different industries and companies.

## Significance
This community represents the foundational leadership approach that has driven India's emergence as a global business power, influencing multiple generations of entrepreneurs and business leaders.
```

**Community 2 Report:**
```markdown
# Business Strategy and Practices

## Summary  
This community encompasses the core strategic approaches and methodologies employed by successful Indian businesses. It highlights distinctive practices that differentiate Indian business strategy from global norms.

## Key Practices
- **Stakeholder Capitalism**: Prioritizing multiple stakeholder groups rather than shareholder primacy
- **Cultural Sensitivity**: International expansion strategies that respect local cultures
- **Frugal Innovation**: Creating high-quality, affordable solutions for diverse markets
- **Sustainable Growth**: Long-term value creation over short-term profits

## Strategic Impact
These practices have enabled Indian companies to compete globally while maintaining strong domestic roots and social responsibility commitments.

## Market Applications
The strategies have proven effective across multiple sectors including technology, manufacturing, and services, providing a replicable framework for business growth.
```

---

## Step 8: Final Artifacts Generation

The system creates query-optimized data structures for both Local and Global search.

### Entity Artifacts (Local Search)

**Entity Record Example:**
```json
{
  "title": "Ratan Tata",
  "id": "uuid-entity-001",
  "type": "PERSON",
  "description": "Prominent Indian business leader known for long-term thinking and social responsibility",
  "degree": 3,
  "text_unit_ids": ["text_unit_001"],
  "communities": [1],
  "graph_embedding": null
}
```

### Relationship Artifacts (Local Search)

**Relationship Record Example:**
```json
{
  "source": "Ratan Tata",
  "target": "Indian Business Leadership",
  "source_id": "uuid-entity-001",
  "target_id": "uuid-entity-004",
  "id": "uuid-rel-001",
  "description": "Ratan Tata exemplifies Indian business leadership patterns",
  "rank": 6,
  "text_unit_ids": ["text_unit_001"],
  "source_degree": 3,
  "target_degree": 3
}
```

### Enhanced Text Units (Local Search)

**Enriched Text Unit:**
```json
{
  "id": "uuid-text-unit-001",
  "document_id": "uuid-doc-001",
  "text_unit": "Indian Business Leadership Patterns\n\nSuccessful Indian business leaders demonstrate unique characteristics that blend traditional values with modern business practices. Leaders like Ratan Tata, N.R. Narayana Murthy, and Azim Premji share common traits of long-term thinking and social responsibility.",
  "entity_ids": ["uuid-entity-001", "uuid-entity-002", "uuid-entity-004"],
  "relationship_ids": ["uuid-rel-001", "uuid-rel-002"]
}
```

### Community Reports (Global Search)

**Query-Ready Community Report:**
```json
{
  "level": 0,
  "community_id": 1,
  "entities": ["uuid-entity-001", "uuid-entity-002", "uuid-entity-003", "uuid-entity-004"],
  "title": "Indian Business Leadership Community",
  "summary": "This community centers around prominent Indian business leaders who have shaped modern business practices in India.",
  "rating": 7.5,
  "rating_explanation": "High impact due to significant influence on business practices and economic development",
  "content": "# Indian Business Leadership Community\n\n## Summary\nThis community centers around prominent Indian business leaders who have shaped modern business practices in India...\n\n## Findings\n\n### Long-term Vision Focus\nThe leaders consistently demonstrate long-term thinking over short-term gains [Data: Entities (1, 2, 3); Relationships (1, 2, 3)].\n\n### Social Responsibility Integration\nAll leaders integrate social responsibility into core business strategy [Data: Entities (1, 2, 3); Relationships (4, 5)]."
}
```

---

## Query Examples Using Generated Artifacts

### Local Search Query

**Query**: "What leadership characteristics does Ratan Tata demonstrate?"

**Data Retrieved**:
1. **Entity**: Ratan Tata record with attributes and connections
2. **Relationships**: All relationships involving Ratan Tata
3. **Text Units**: Original text mentioning Ratan Tata with entity annotations
4. **Connected Entities**: Indian Business Leadership, Stakeholder Capitalism

**Generated Response**: 

*"Ratan Tata demonstrates several key leadership characteristics including long-term thinking and social responsibility [Data: Entities (1); Relationships (1); Sources (1)]. His leadership exemplifies Indian business leadership patterns that blend traditional values with modern business practices, as evidenced by his approach to stakeholder capitalism and international expansion [Data: Entities (1, 4); Relationships (1, 4)]."*

### Global Search Query

**Query**: "What are the patterns in Indian business leadership approaches?"

**Data Retrieved**:
1. **Community Reports**: Business Leadership Community summary
2. **Key Points**: Extracted strategic insights across the community
3. **Cross-Community Analysis**: Connections to Business Practices community

**Generated Response**:

*"Indian business leadership demonstrates several distinctive patterns [Data: Reports (1, 2)]. Leaders consistently emphasize long-term value creation over short-term gains, integrate social responsibility into core business strategy, and blend traditional values with modern practices. This approach manifests through stakeholder capitalism initiatives and culturally-sensitive international expansion strategies [Data: Reports (1, 2, +more)]."*

---

## Understanding Your Data

### Data Size Expectations

For a **typical business document collection**:

| Input | Typical Output Volume |
|-------|----------------------|
| **10 documents** (5-10 pages each) | 50-100 text units |
| **Text Units** | 150-300 entities |
| **Entities** | 200-400 relationships |
| **Communities** | 8-15 communities |
| **Reports** | 8-15 comprehensive summaries |

### Quality Indicators

**Good Entity Extraction**:
- Specific, well-defined entity names
- Accurate type classification (PERSON, ORGANIZATION, CONCEPT)
- Meaningful descriptions tied to source content

**Strong Relationships**:
- Clear, meaningful relationship descriptions
- High rank scores for important connections
- Logical directional relationships

**Coherent Communities**:
- Meaningful thematic groupings of related entities
- Logical groupings that make business sense
- Reasonable community sizes (3-12 entities)

### Debugging Your Pipeline

**Common Issues & Solutions**:

- **Low Entity Count**: Increase chunk size or use more detailed documents
- **Weak Relationships**: Ensure documents contain explicit connections between concepts
- **Poor Communities**: Check if entities are well-connected; isolated entities won't cluster well
- **Generic Descriptions**: Use domain-specific documents with detailed explanations

---

## Related Documentation

**[Documentation Index](../index.md)**  
Return to documentation overview

---

## Related Resources

- **[Architecture Overview](../architecture/overview.md)** - System design and concepts
- **[Indexing Pipeline](indexing_pipeline.md)** - Technical implementation
- **[Query System](query_system.md)** - Search strategies
- **[Advanced Examples](graph_extraction/index.md)** - Component-level customization 