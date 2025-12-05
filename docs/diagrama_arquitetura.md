# Diagrama de Arquitetura - MAS para Plataforma de Ensino

## Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Web UI)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Consultas │  │    CQs    │  │ Reasoner │  │  Sobre   │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼─────────────┼──────────────┼──────────────┼─────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │      API REST (FastAPI)       │
        │  ┌─────────────────────────┐ │
        │  │  /query                  │ │
        │  │  /cq/{n}                 │ │
        │  │  /reasoner/{op}          │ │
        │  │  /sparql                 │ │
        │  └─────────────────────────┘ │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Agent Orchestrator           │
        │   (LangGraph)                  │
        │                                │
        │  ┌──────────────────────────┐ │
        │  │      Router Node          │ │
        │  └───────────┬──────────────┘ │
        │              │                 │
        │  ┌───────────┴───────────┐    │
        │  │                       │    │
        │  ▼                       ▼    │
        │  ┌──────────┐    ┌──────────┐ │
        │  │Coordinator│    │   LMS    │ │
        │  └──────────┘    └──────────┘ │
        │  ┌──────────┐    ┌──────────┐ │
        │  │Recommend │    │ Student  │ │
        │  └──────────┘    └──────────┘ │
        └───────────────┬───────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐            ┌──────────────────┐
│  RAG Híbrido  │            │  DL Reasoner     │
│               │            │  (HermiT)        │
│  ┌─────────┐  │            │                  │
│  │ Vector  │  │            │  - Classificação │
│  │ Store   │  │            │  - Realização    │
│  │ (FAISS) │  │            │  - Consistência  │
│  └────┬────┘  │            │  - Materialização│
│       │       │            └────────┬─────────┘
│  ┌────┴────┐  │                     │
│  │ SPARQL  │  │                     │
│  │ Engine  │  │                     │
│  └────┬────┘  │                     │
└───────┼───────┘                     │
        │                              │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Ontologia OWL 2 DL │
        │   (ontologia_mora.owl)│
        │                      │
        │  - 47 Classes       │
        │  - 88 Propriedades │
        │  - Instâncias      │
        └──────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                      │
        ▼                      ▼
┌──────────────┐    ┌─────────────────┐
│  Documentos  │    │   Triplestore   │
│  (Markdown)  │    │   (RDF Graph)   │
│              │    │                 │
│  - RAG docs  │    │  - Instâncias   │
│  - Metadata  │    │  - Relações     │
└──────────────┘    └─────────────────┘
```

## Fluxo de Dados

### 1. Consulta do Usuário
```
Usuário → Frontend → API REST → Orchestrator
```

### 2. Roteamento
```
Orchestrator → Router → Agente Apropriado
  (Coordinator/LMS/Recommendation/Student)
```

### 3. Recuperação de Contexto
```
Agente → HybridRetriever
  ├─→ VectorStore (FAISS) → Documentos relevantes
  └─→ SPARQLQueryEngine → Dados estruturados da ontologia
```

### 4. Verificação de Consistência
```
HybridRetriever → DLReasoner → Verificação ontológica
```

### 5. Geração de Resposta
```
Agente → LLM (com contexto) → Resposta citada
```

### 6. Retorno
```
Agente → Orchestrator → API → Frontend → Usuário
```

## Componentes Principais

### Camada de Apresentação
- **Frontend Web**: Interface HTML/CSS/JavaScript
- **API REST**: FastAPI com endpoints RESTful

### Camada de Agentes
- **Orchestrator**: LangGraph para orquestração
- **4 Agentes**: Coordinator, LMS, Recommendation, Student

### Camada de RAG
- **HybridRetriever**: Combina vector search + SPARQL
- **VectorStore**: FAISS para busca semântica
- **SPARQLQueryEngine**: Consultas estruturadas

### Camada de Conhecimento
- **Ontologia OWL 2 DL**: Base de conhecimento semântica
- **DLReasoner**: HermiT para inferências
- **Documentos**: Base documental para RAG

## Integrações

- **LangChain**: Framework para LLMs e RAG
- **LangGraph**: Orquestração de agentes
- **FAISS**: Vector store para embeddings
- **RDFLib**: Manipulação RDF/SPARQL
- **Owlready2**: Integração com reasoners DL
- **FastAPI**: API REST
- **Sentence Transformers**: Embeddings

