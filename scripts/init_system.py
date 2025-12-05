"""
Script para inicializar o sistema completo.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.load_documents import main as load_docs
from rag.vector_store import VectorStore
from rag.sparql_query import SPARQLQueryEngine
from rag.hybrid_retriever import HybridRetriever


def check_ontology():
    """Verifica se a ontologia existe."""
    ontology_path = "ontologia_mora.owl"
    if not os.path.exists(ontology_path):
        print(f"ERRO: Ontologia não encontrada em {ontology_path}")
        return False
    print(f"✓ Ontologia encontrada: {ontology_path}")
    return True


def check_documents():
    """Verifica se há documentos para carregar."""
    docs_dir = os.path.join("documents", "markdown")
    if not os.path.exists(docs_dir):
        print(f"AVISO: Diretório de documentos não encontrado: {docs_dir}")
        return False
    
    files = [f for f in os.listdir(docs_dir) if f.endswith('.md')]
    print(f"✓ Documentos encontrados: {len(files)}")
    return True


def initialize_vector_store():
    """Inicializa o vector store."""
    print("\n=== Inicializando Vector Store ===")
    vector_store = VectorStore()
    
    # Verificar se já existe índice
    index_path = os.path.join(vector_store.store_path, "index.faiss")
    if os.path.exists(index_path):
        print("Carregando índice existente...")
        vector_store.load()
        print(f"✓ Índice carregado com {len(vector_store.documents)} chunks")
    else:
        print("Nenhum índice encontrado. Execute load_documents.py primeiro.")
    
    return vector_store


def initialize_sparql():
    """Inicializa o motor SPARQL."""
    print("\n=== Inicializando SPARQL Engine ===")
    try:
        engine = SPARQLQueryEngine()
        print("✓ SPARQL Engine inicializado")
        return engine
    except Exception as e:
        print(f"ERRO ao inicializar SPARQL: {e}")
        return None


def test_hybrid_retriever(vector_store, sparql_engine):
    """Testa o retriever híbrido."""
    print("\n=== Testando Hybrid Retriever ===")
    retriever = HybridRetriever(vector_store, sparql_engine)
    
    # Teste simples
    test_query = "Quais cursos estão disponíveis?"
    results = retriever.retrieve(test_query, k=3)
    
    print(f"Query de teste: '{test_query}'")
    print(f"Resultados vetoriais: {len(results['vector_results'])}")
    print(f"Resultados SPARQL: {len(results['sparql_results'])}")
    print(f"Citações de documentos: {len(results['citations']['documents'])}")
    print(f"Citações de IRIs: {len(results['citations']['iris'])}")
    print("✓ Hybrid Retriever funcionando")


def main():
    """Inicializa o sistema completo."""
    print("=" * 60)
    print("Inicializando Sistema MAS para Plataforma de Ensino")
    print("=" * 60)
    
    # Verificações
    if not check_ontology():
        print("\nERRO: Sistema não pode ser inicializado sem ontologia.")
        return
    
    check_documents()
    
    # Inicializar componentes
    vector_store = initialize_vector_store()
    sparql_engine = initialize_sparql()
    
    if vector_store and sparql_engine:
        test_hybrid_retriever(vector_store, sparql_engine)
    
    print("\n" + "=" * 60)
    print("Inicialização concluída!")
    print("=" * 60)
    print("\nPróximos passos:")
    print("1. Execute 'python scripts/load_documents.py' para indexar documentos")
    print("2. Execute 'python scripts/run_cqs.py' para testar CQs")
    print("3. Execute 'python -m api.main' para iniciar a API")


if __name__ == "__main__":
    main()

