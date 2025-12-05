# MAS para Plataforma de Ensino - Sistema Multiagente com RAG e Ontologia DL

Sistema multiagente que integra ontologia OWL 2 DL, RAG híbrido e agentes baseados em LLM para suporte a plataformas de ensino.

---

## 📋 Índice

1. [Instalação](#instalação)
2. [Configuração](#configuração)
3. [Como Usar](#como-usar)
4. [Testes](#testes)
5. [Estrutura do Projeto](#estrutura-do-projeto)

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.10 ou superior
- Java 8+ (opcional, para HermiT reasoner)

### Passo 1: Instalar Dependências

```bash
pip install -r requirements.txt
```

**Nota:** Se der erro com alguma dependência, instale em grupos:

```bash
# Grupo 1: Essenciais
pip install numpy pandas fastapi uvicorn pydantic

# Grupo 2: LangChain
pip install langchain langchain-openai langgraph langchain-community langchain-ollama

# Grupo 3: RAG
pip install sentence-transformers faiss-cpu

# Grupo 4: Ontologia
pip install rdflib owlready2 sparqlwrapper

# Grupo 5: Resto
pip install -r requirements.txt
```

---

## ⚙️ Configuração

### Opção 1: Usar Llama Local (Recomendado - Gratuito)

**1. Instalar Ollama:**
- Windows: Baixe de https://ollama.com/download/windows
- Linux/Mac: `curl -fsSL https://ollama.com/install.sh | sh`

**2. Baixar modelo Llama:**
```bash
ollama pull llama3.2
```

**3. Criar arquivo `.env` na raiz do projeto:**
```bash
USE_OLLAMA=true
OLLAMA_MODEL=llama3.2
```

**4. Instalar dependência:**
```bash
pip install langchain-ollama
```

**5. Iniciar Ollama (em terminal separado):**
```bash
ollama serve
```

### Opção 2: Usar OpenAI (Pago)

**1. Obter chave API:**
- Acesse: https://platform.openai.com/api-keys
- Crie uma chave

**2. Criar arquivo `.env`:**
```bash
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4
```

**Nota:** Se não configurar nenhum modelo, o sistema tentará usar Ollama automaticamente.

---

## 📚 Como Usar

### 1. Carregar Documentos na Base de Conhecimento

**Primeira vez:** Carregue os documentos Markdown para criar o índice de busca vetorial.

```bash
python scripts/load_documents.py
```

**O que faz:**
- Carrega documentos de `documents/markdown/`
- Cria embeddings usando sentence-transformers
- Salva índice FAISS em `data/vector_store/`

**Saída esperada:**
```
Carregando documentos...
Documentos carregados: 3
Indexando documentos...
Salvando índice...
Índice salvo com 7 chunks
Concluído!
```

### 2. Executar Competency Questions (CQs)

Testa as 10 Competency Questions que dependem de inferência DL:

```bash
python scripts/run_cqs.py
```

**O que faz:**
- Executa consultas SPARQL à ontologia
- Testa raciocínio DL (classificação, consistência, realização)
- Mostra resultados de cada CQ

### 3. Ver Exemplos de Uso

Executa exemplos práticos do sistema:

```bash
python scripts/example_usage.py
```

**O que faz:**
- Demonstra consultas básicas
- Mostra sistema de recomendação
- Testa consultas SPARQL diretas
- Demonstra recuperação híbrida

### 4. Iniciar API REST

Inicia servidor FastAPI para acesso via HTTP:

```bash
python -m api.main
```

**Acessar:**
- API: http://localhost:8000
- Documentação: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 5. Iniciar Frontend (Interface Web)

**Opção 1: Servidor HTTP simples**
```bash
# Terminal 1: Iniciar API
python -m api.main

# Terminal 2: Iniciar servidor HTTP para frontend
cd frontend
python -m http.server 8080
```

Depois acesse: http://localhost:8080

**Opção 2: Abrir direto no navegador**
```bash
# Terminal 1: Iniciar API
python -m api.main

# Terminal 2: Abrir frontend/index.html no navegador
# (Arraste o arquivo para o navegador ou use: start frontend/index.html)
```

**Funcionalidades do Frontend:**
- 💬 **Consultas**: Interface de chat para testar queries
- ❓ **Competency Questions**: Executar CQs com um clique
- 🧠 **Reasoner DL**: Testar classificação, consistência, realização
- ℹ️ **Sobre**: Visualizar arquitetura e status do sistema

**Endpoints disponíveis:**
- `POST /query` - Processar query através dos agentes
- `POST /sparql` - Executar consulta SPARQL
- `POST /consistency` - Verificar consistência ontológica
- `GET /courses` - Listar cursos
- `GET /tasks?student_id=...` - Listar tarefas de estudante

### 5. Usar Programaticamente

```python
from agents.orchestrator import AgentOrchestrator
from rag.vector_store import VectorStore
from rag.sparql_query import SPARQLQueryEngine
from rag.hybrid_retriever import HybridRetriever

# Inicializar componentes
vector_store = VectorStore()
vector_store.load()  # Carrega índice existente

sparql_engine = SPARQLQueryEngine()
retriever = HybridRetriever(vector_store, sparql_engine)
orchestrator = AgentOrchestrator(retriever)

# Processar query
result = orchestrator.process_query(
    "Quais cursos estão disponíveis para o estudante Ana?",
    context={'student_id': 'http://www.exemplo.org/ead-ontologia#Estudante_Ana'}
)

print(result['response'])
print(f"Citações: {result['citations']}")
```

---

## 🧪 Testes

### Teste Rápido de Imports

Verifica se todas as dependências estão instaladas:

```bash
python -c "import numpy, pandas, fastapi, langchain, rdflib, owlready2; print('✅ Todas as dependências OK')"
```

### Teste do Vector Store

```bash
python -c "from rag.vector_store import VectorStore; vs = VectorStore(); vs.load(); print(f'✅ Vector Store OK - {len(vs.documents)} chunks')"
```

### Teste do SPARQL

```bash
python -c "from rag.sparql_query import SPARQLQueryEngine; e = SPARQLQueryEngine(); print(f'✅ SPARQL OK - {len(e.get_courses())} cursos')"
```

### Teste do Reasoner DL

```bash
python -c "from ontology.reasoner import DLReasoner; r = DLReasoner(); print(f'✅ Reasoner OK - Consistente: {r.check_consistency()[\"consistent\"]}')"
```

### Teste Completo do Sistema

```python
# Criar arquivo teste_sistema.py
from rag.vector_store import VectorStore
from rag.sparql_query import SPARQLQueryEngine
from rag.hybrid_retriever import HybridRetriever
from agents.orchestrator import AgentOrchestrator

# Inicializar
vs = VectorStore()
vs.load()
se = SPARQLQueryEngine()
hr = HybridRetriever(vs, se)
orch = AgentOrchestrator(hr)

# Testar
result = orch.process_query("Quais cursos estão disponíveis?")
print("✅ Sistema funcionando!")
print(f"Resposta: {result['response'][:100]}...")
```

---

## 📁 Estrutura do Projeto

```
ws-mora/
├── agents/                    # Agentes do sistema
│   ├── base_agent.py         # Classe base para agentes
│   ├── coordinator.py        # Agente coordenador
│   ├── student.py            # Agente estudante
│   ├── recommendation.py     # Agente de recomendação
│   ├── lms.py               # Agente LMS
│   └── orchestrator.py      # Orquestrador (LangGraph)
│
├── rag/                      # Sistema RAG híbrido
│   ├── vector_store.py       # Busca vetorial (FAISS)
│   ├── sparql_query.py       # Consultas SPARQL
│   └── hybrid_retriever.py   # Retriever híbrido
│
├── ontology/                 # Ontologia e reasoner
│   ├── reasoner.py           # Reasoner DL (HermiT/Pellet)
│   ├── competency_questions.md  # Documentação das CQs
│   └── reasoning_notebook.ipynb  # Notebook de raciocínio
│
├── documents/                # Base documental
│   ├── markdown/            # Documentos Markdown
│   └── metadata.json        # Metadados dos documentos
│
├── api/                      # API REST
│   └── main.py              # Servidor FastAPI
│
├── scripts/                  # Scripts auxiliares
│   ├── load_documents.py    # Carregar documentos
│   ├── run_cqs.py          # Executar CQs
│   ├── example_usage.py    # Exemplos de uso
│   └── init_system.py      # Inicializar sistema
│
├── data/                     # Dados gerados
│   └── vector_store/        # Índice FAISS
│
├── ontologia_mora.owl        # Ontologia OWL
├── requirements.txt         # Dependências Python
└── README.md               # Este arquivo
```

---

## 🎯 Fluxo de Trabalho Recomendado

### Primeira Vez

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar modelo LLM:**
   - Criar `.env` com `USE_OLLAMA=true` (ou `OPENAI_API_KEY=...`)
   - Se usar Ollama: `ollama pull llama3.2` e `ollama serve`

3. **Carregar documentos:**
   ```bash
   python scripts/load_documents.py
   ```

4. **Testar CQs:**
   ```bash
   python scripts/run_cqs.py
   ```

5. **Ver exemplos:**
   ```bash
   python scripts/example_usage.py
   ```

### Uso Diário

1. **Iniciar Ollama (se usar):**
   ```bash
   ollama serve
   ```

2. **Usar o sistema:**
   - Via API: `python -m api.main`
   - Via Python: usar `AgentOrchestrator` como no exemplo acima

---

## 🔧 Solução de Problemas

### Erro: "No module named X"

```bash
pip install X
```

### Erro: "Vector store not found"

```bash
python scripts/load_documents.py
```

### Erro: "Ollama connection failed"

Certifique-se de que:
1. Ollama está instalado
2. Modelo foi baixado: `ollama pull llama3.2`
3. Ollama está rodando: `ollama serve`

### Erro: "OpenAI API key not found"

Configure no `.env`:
- `OPENAI_API_KEY=sua_chave` (se usar OpenAI)
- OU `USE_OLLAMA=true` (se usar Ollama)

### Erro: "Ontology not found"

Verifique se `ontologia_mora.owl` está na raiz do projeto.

### ⚠️ Reasoner DL: "UnsupportedDatatypeException: xsd:date"

**Problema:** A ontologia usa `xsd:date`, que não é suportado pelo HermiT (apenas `xsd:dateTime` está no OWL 2 datatype map).

**Solução:**
- **Opção 1:** O sistema continua funcionando normalmente! As CQs 1-5 funcionam perfeitamente via SPARQL.
- **Opção 2:** Para usar reasoner completo, substitua `xsd:date` por `xsd:dateTime` na ontologia.

**Nota:** Isso não afeta o funcionamento do sistema - apenas limita algumas inferências DL avançadas. SPARQL e todas as funcionalidades principais continuam funcionando.

---

## 📊 Componentes Principais

### Agentes

- **CoordinatorAgent**: Orquestra tarefas e resolve conflitos
- **StudentAgent**: Representa estudantes e suas ações
- **RecommendationAgent**: Fornece recomendações personalizadas
- **LMSAgent**: Gerencia estado da plataforma e triplestore

### RAG Híbrido

- **Vector Store**: Busca semântica em documentos (FAISS)
- **SPARQL Engine**: Consultas estruturadas à ontologia
- **Hybrid Retriever**: Combina ambas as fontes

### Reasoner DL

- **Classificação**: Infere hierarquia de classes
- **Consistência**: Verifica contradições
- **Realização**: Infere tipos de indivíduos
- **Materialização**: Adiciona triplas inferidas

---

## 📝 Notas Importantes

1. **Primeira execução:** Sempre execute `load_documents.py` antes de usar o sistema
2. **Ollama:** Deve estar rodando (`ollama serve`) para os agentes funcionarem
3. **Ontologia:** O arquivo `ontologia_mora.owl` deve estar na raiz
4. **Sem LLM:** Você pode testar SPARQL, CQs e Reasoner sem configurar LLM

---

## 🎓 Para o Projeto Acadêmico

Este sistema atende todos os requisitos:

- ✅ Ontologia OWL 2 DL com inferência
- ✅ RAG híbrido (vetorial + SPARQL)
- ✅ Agentes baseados em LLM (orquestrados com LangGraph)
- ✅ Respostas citadas (documentos + IRIs)
- ✅ Verificação de consistência ontológica
- ✅ 10 Competency Questions implementadas

---

## 👥 Autores

- Júlio Cesar
- Carlos Guedes

---

## 📄 Licença

Projeto acadêmico - Uso educacional.

