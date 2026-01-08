# Memory Architecture

Itqahn's memory system ensures agents maintain context, learn from past decisions, and avoid repeating mistakes.

---

## Memory Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                     MEMORY ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Working Memory │  │ Episodic Memory │  │ Semantic Memory │  │
│  │  (Workflow)     │  │ (Vector Store)  │  │ (Knowledge Graph│  │
│  │                 │  │                 │  │                 │  │
│  │ • Current task  │  │ • Past PRDs     │  │ • Architecture  │  │
│  │ • Conversation  │  │ • Past ADRs     │  │   patterns      │  │
│  │ • Active state  │  │ • Past incidents│  │ • Domain models │  │
│  │                 │  │ • Code snippets │  │ • Relationships │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
│           │                    │                    │            │
│           └────────────────────┼────────────────────┘            │
│                                │                                 │
│                    ┌───────────▼───────────┐                    │
│                    │    Memory Router      │                    │
│                    │  (Context Assembly)   │                    │
│                    └───────────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Working Memory (Temporal Workflow State)

**Purpose**: Current task context within a workflow.

| Content | Persistence | Scope |
|---------|-------------|-------|
| Current task | Workflow duration | Single workflow |
| Conversation history | Workflow duration | Single workflow |
| Active variables | Workflow duration | Single workflow |
| Pending decisions | Until resolved | Single workflow |

**Implementation**:
- Stored in Temporal workflow state
- Automatically persisted and recovered
- Cleared when workflow completes

**Size limits**:
- Max workflow history: 50,000 events
- Max state size: 2MB
- Use `continue_as_new` for long workflows

---

## Episodic Memory (Vector Store / RAG)

**Purpose**: Retrievable past experiences.

| Content | Retention | Access Pattern |
|---------|-----------|----------------|
| Past PRDs | Indefinite | Semantic search |
| Past ADRs | Indefinite | Semantic search |
| Incident reports | 2 years | Semantic search |
| Code snippets | Per-project | Semantic search |
| User feedback | 1 year | Semantic search |

**Implementation**:
- Vector database (pgvector, Pinecone, or Weaviate)
- Embeddings generated at write time
- Top-k retrieval with similarity threshold

**Indexing strategy**:

```yaml
episodic_memory:
  collections:
    - name: requirements
      source: requirements/*.md
      chunking: section-based
      embedding_model: text-embedding-3-large

    - name: decisions
      source: docs/99-appendix/adrs/*.md
      chunking: document-level
      embedding_model: text-embedding-3-large

    - name: incidents
      source: postmortems/*.md
      chunking: section-based
      embedding_model: text-embedding-3-large

    - name: code
      source: src/**/*.{ts,py,go}
      chunking: function-level
      embedding_model: code-embedding-model
```

**Retrieval policy**:
- Retrieve top 5 most similar documents
- Similarity threshold: 0.7 minimum
- Re-rank with cross-encoder for precision

---

## Semantic Memory (Knowledge Graph)

**Purpose**: Structured knowledge about the domain.

| Content | Structure | Updates |
|---------|-----------|---------|
| Architecture patterns | Entity-relationship | On ADR acceptance |
| Domain models | Entity-attribute | On schema changes |
| Service dependencies | Graph edges | Auto-discovered |
| Team ownership | Entity-relationship | From CODEOWNERS |

**Implementation**:
- Graph database (Neo4j, AWS Neptune, or embedded)
- Schema defined in ontology files
- Updated by Documentation Librarian agent

**Example entities**:

```cypher
// Services and dependencies
(:Service {name: "user-service"})
  -[:DEPENDS_ON]->(:Service {name: "auth-service"})
  -[:OWNED_BY]->(:Team {name: "identity-team"})

// Data models
(:Entity {name: "User"})
  -[:HAS_ATTRIBUTE]->(:Attribute {name: "email", type: "string", pii: true})
  -[:REFERENCES]->(:Entity {name: "Organization"})

// Patterns
(:Pattern {name: "saga-pattern"})
  -[:USED_IN]->(:Service {name: "order-service"})
  -[:DOCUMENTED_IN]->(:ADR {id: "ADR-0042"})
```

**Query patterns**:
- "What services depend on auth-service?"
- "Which entities contain PII?"
- "What patterns are used in the order domain?"

---

## Memory Router

The Memory Router assembles context for agent prompts:

```python
async def assemble_context(query: str, agent_role: str) -> Context:
    # 1. Get working memory (current workflow state)
    working = await temporal.get_workflow_state()

    # 2. Retrieve relevant episodic memory
    episodic = await vector_store.search(
        query=query,
        collections=get_collections_for_role(agent_role),
        top_k=5,
        threshold=0.7
    )

    # 3. Query semantic memory for relationships
    semantic = await knowledge_graph.query(
        extract_entities(query),
        depth=2
    )

    # 4. Assemble and prioritize
    return Context(
        working_memory=working,
        relevant_past=episodic,
        domain_knowledge=semantic,
        token_budget=calculate_budget(agent_role)
    )
```

---

## Memory Policies

### Retention

| Memory Type | Default Retention | Regulated Tier |
|-------------|-------------------|----------------|
| Working | Workflow lifetime | + 90 days audit |
| Episodic | 2 years | 7 years |
| Semantic | Indefinite | Indefinite |

### Access Control

| Memory Type | Who Can Read | Who Can Write |
|-------------|--------------|---------------|
| Working | Workflow agents | Workflow agents |
| Episodic | All agents (filtered) | Specific agents |
| Semantic | All agents | Documentation Librarian |

### Privacy

| Rule | Implementation |
|------|----------------|
| No PII in episodic memory | Scrubbing pipeline before indexing |
| Tenant isolation | Separate vector namespaces per tenant |
| Right to erasure | Delete by tenant/user ID |

---

## Preventing Memory Pollution

### Anti-patterns to detect

| Anti-pattern | Detection | Prevention |
|--------------|-----------|------------|
| Hallucinated facts | Cross-reference with graph | Require source citation |
| Contradictory decisions | ADR conflict detection | Require explicit supersede |
| Outdated patterns | Age-based decay | Mark deprecated in graph |
| Circular reasoning | Citation loop detection | Break loops in retrieval |

### Quality gates

Before writing to long-term memory:

1. **Validation**: Does this follow the schema?
2. **Deduplication**: Is this already stored?
3. **Conflict check**: Does this contradict existing knowledge?
4. **Source verification**: Is the source authoritative?

---

## Memory in Agent Workflows

### At workflow start

```
1. Load working memory (empty or continued)
2. Retrieve relevant episodic memory for task
3. Query semantic memory for domain context
4. Assemble initial prompt context
```

### During workflow

```
1. Update working memory after each activity
2. Optionally persist insights to episodic memory
3. Update semantic memory on significant decisions
```

### At workflow end

```
1. Archive working memory (if audit required)
2. Index final artifacts to episodic memory
3. Update semantic memory with new relationships
4. Clear working memory state
```

---

## Related Documents

- `docs/02-architecture/workflow-architecture.md` — Temporal state management
- `docs/08-agents/agent-system-contract.md` — Agent memory access rules
- `docs/05-compliance/audit-ready-operations.md` — Memory retention for audit

---

**Version**: 2.0.0 | **Date**: 2026-01-06
